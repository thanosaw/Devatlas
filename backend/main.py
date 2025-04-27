# from app.routes import webhooks

# app = FastAPI()
# app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

from fastapi import FastAPI, Request, Depends, HTTPException, Query
import logging
import uvicorn
from backend.routes.webhooks import router as webhooks_router
from backend.services.github_processor import GitHubProcessor
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import the GitHub fetcher
from backend.services.github_fetch import fetch_and_save_all_pull_requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LA Hacks 2025 Webhook Handler")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Server started")
    logger.info(f"Actions file path: actions.json")
    logger.info("Supported webhook events: pull_request, issues, issue_comment, pull_request_review, "
                "pull_request_review_comment, discussion, discussion_comment, label, push")

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {"status": "ok", "message": "GitHub webhook handler is running"}

# Include the webhooks router
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])

@app.get("/fetch-pull-requests/{owner}/{repo}")
async def fetch_all_prs(owner: str, repo: str):
    """
    Fetch all pull requests from a GitHub repository and save them to collective.json.
    
    This endpoint fetches all pull requests for the specified repository,
    formats them with fields: id, number, title, body, state, createdAt,
    and saves them to a file called collective.json.
    
    Args:
        owner: Repository owner/organization (e.g., "facebook")
        repo: Repository name (e.g., "react")
        
    Returns:
        Information about the fetched pull requests
    """
    print("Fetching pull requests...")
    # if not os.environ.get("GITHUB_TOKEN"):
    #     raise HTTPException(status_code=500, detail="GitHub token not configured")
    
    try:
        # Fetch all PRs and save to collective.json
        result = fetch_and_save_all_pull_requests(owner, repo)
        
        # Return information about the fetched data
        return {
            "status": "success",
            "repository": result["repository"],
            "timestamp": result["timestamp"],
            "count": result["count"],
            "file": "collective.json",
            "message": f"Successfully fetched and saved {result['count']} pull requests"
        }
    except Exception as e:
        logger.error(f"Error fetching pull requests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching pull requests: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)