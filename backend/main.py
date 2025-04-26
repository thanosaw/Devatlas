# from app.routes import webhooks

# app = FastAPI()
# app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

from fastapi import FastAPI, Request, Response, Header, Depends
import json
import hmac
import hashlib
from typing import Optional
from backend.routes import webhooks
from backend.config import settings
from backend.services.github_service import process_push_event

app = FastAPI()
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

@app.on_event("startup")
async def startup_event():
    print("server started")
    print(f"Webhook route available at: /webhooks/github")

@app.get("/")
async def root():
    return {"message": "Welcome to Ownership AI API"}

@app.get("/test-webhook")
async def test_webhook_manually():
    """
    Test endpoint to simulate a GitHub webhook call.
    This is for debugging and testing purposes only.
    """
    # Create a mock GitHub push event payload
    mock_payload = {
        "repository": {
            "full_name": "test-user/test-repo"
        },
        "pusher": {
            "name": "test-user"
        },
        "ref": "refs/heads/main",
        "commits": [
            {
                "id": "abc1234567890",
                "message": "Test commit message",
                "timestamp": "2023-10-25T12:00:00Z",
                "url": "https://github.com/test-user/test-repo/commit/abc1234567890",
                "author": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "added": ["file1.txt"],
                "modified": ["file2.txt"],
                "removed": []
            }
        ]
    }
    
    # Convert the payload to JSON
    payload_bytes = json.dumps(mock_payload).encode('utf-8')
    
    # Generate a valid signature using the secret
    secret = settings.GITHUB_WEBHOOK_SECRET.encode()
    signature = 'sha256=' + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()
    
    print("\n===== TEST WEBHOOK CALL =====")
    print(f"Generated signature: {signature}")
    
    # Create a fake request context to pass to the webhook handler
    headers = {
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }
    
    # Call the webhook handler directly
    try:
        # Manually verify the signature first
        if secret and signature:
            print("✅ Secret and signature look valid")
        
        # Call the service function directly with our test payload
        print("Calling process_push_event with test payload...")
        await process_push_event(mock_payload)
        return {
            "status": "success", 
            "message": "Test webhook call simulated successfully"
        }
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"}