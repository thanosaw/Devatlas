# from app.routes import webhooks

# app = FastAPI()
# app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

from fastapi import FastAPI, Request
import logging
import uvicorn
from backend.routes.webhooks import router as webhooks_router
from backend.services.github_processor import GitHubProcessor
from backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LA Hacks 2025 Webhook Handler")

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Server started")
    logger.info(f"Actions file path: {settings.ACTIONS_FILE_PATH}")
    logger.info("Supported webhook events: pull_request, issues, issue_comment, pull_request_review, "
                "pull_request_review_comment, discussion, discussion_comment, label, push")

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {"status": "ok", "message": "GitHub webhook handler is running"}

# Include the webhooks router
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)