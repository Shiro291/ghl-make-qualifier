from fastapi import APIRouter, HTTPException, Depends
from src.core.models import InboundLead
from src.ai.llm_qualifier import qualify_lead
from src.services.billing import check_and_increment_usage
from src.services.dlq import send_to_dlq
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def verify_billing_limit():
    if not check_and_increment_usage():
        raise HTTPException(status_code=429, detail="Monthly limit reached. Please upgrade your tier.")

@router.post("/webhook/meta-lead")
async def handle_meta_lead(lead: InboundLead, _: None = Depends(verify_billing_limit)):
    """
    Simulates a webhook listener receiving a payload from Meta or a Landing Page.
    """
    logger.info(f"Received lead: {lead.name} ({lead.email})")
    
    try:
        qualification = await qualify_lead(lead.inquiry_text)
    except Exception as e:
        logger.error(f"LLM Qualification failed: {str(e)}")
        # Send to DLQ and fallback
        send_to_dlq(lead.model_dump(), f"LLM Error: {str(e)}")
        return {
            "success": False,
            "message": "AI Engine unavailable. Lead routed to manual queue (DLQ).",
            "route_action": "Sent to Dead Letter Queue"
        }
        
    logger.info(f"Qualification result: {qualification.model_dump_json()}")
    
    # State Machine Routing logic
    if qualification.status == "qualified":
        logger.info(f"ROUTING -> GoHighLevel Pipeline: Hot Lead (Score: {qualification.urgency_score})")
        route_action = "Sent to GHL - Hot Lead Pipeline"
    else:
        logger.info("ROUTING -> Slack Alert: Manual Review Required")
        route_action = "Sent to Slack - Manual Review"

    return {
        "success": True,
        "lead_id": "simulated-id-123",
        "qualification": qualification.model_dump(),
        "route_action": route_action
    }
