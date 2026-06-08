import os
import json
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field
from ai.llm_qualifier import qualify_lead

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Lead Automation Engine", version="1.0.0")

# -----------------------------------------------------------------------------
# Error Handling (The 422 Catcher)
# -----------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches 422 Unprocessable Entity errors.
    Instead of dying silently, we format an alert payload that would normally be 
    sent to Slack or Discord to ensure no lead is silently dropped.
    """
    body = await request.body()
    logger.error(f"422 Validation Error. Raw payload: {body.decode('utf-8', errors='ignore')}")
    
    # Mock sending to a Dead Letter Queue or Slack
    alert_payload = {
        "alert": "SCHEMA_VALIDATION_FAILED",
        "errors": exc.errors(),
        "raw_body": body.decode('utf-8', errors='ignore')
    }
    logger.error(f"Sent to internal alert system: {json.dumps(alert_payload)}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Payload schema invalid. Alert dispatched internally."}
    )

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------
class InboundLead(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=8)
    inquiry_text: str = Field(..., min_length=10)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.post("/webhook/meta-lead")
async def handle_meta_lead(lead: InboundLead):
    """
    Simulates a webhook listener receiving a payload from Meta or a Landing Page.
    """
    logger.info(f"Received lead: {lead.name} ({lead.email})")
    
    # 1. LLM Qualification
    try:
        qualification = await qualify_lead(lead.inquiry_text)
    except Exception as e:
        logger.error(f"LLM Qualification failed: {str(e)}")
        # Fallback to manual review
        qualification = {"status": "handoff", "reason": "LLM Engine Error"}
        
    logger.info(f"Qualification result: {qualification}")
    
    # 2. State Machine Routing
    if qualification.get("status") == "qualified":
        # Simulate pushing to GoHighLevel (Hot Lead)
        logger.info(f"ROUTING -> GoHighLevel Pipeline: Hot Lead (Score: {qualification.get('urgency_score')})")
        route_action = "Sent to GHL - Hot Lead Pipeline"
    else:
        # Simulate pushing to Manual Review
        logger.info("ROUTING -> Slack Alert: Manual Review Required")
        route_action = "Sent to Slack - Manual Review"

    return {
        "success": True,
        "lead_id": "simulated-id-123",
        "qualification": qualification,
        "route_action": route_action
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
