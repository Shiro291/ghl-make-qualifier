import logging
import json
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from src.api.routes import router
from src.services.billing import init_billing_db
from src.services.dlq import init_dlq_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Lead Automation Engine", version="1.0.0")

@app.on_event("startup")
def startup_db():
    init_billing_db()
    init_dlq_db()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.error(f"422 Validation Error. Raw payload: {body.decode('utf-8', errors='ignore')}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Payload schema invalid. Alert dispatched internally."}
    )

app.include_router(router)

@app.get("/")
async def serve_frontend():
    try:
        with open("src/frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception:
        return HTMLResponse(content="<h1>Frontend missing</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
