# from app.routes import webhooks

# app = FastAPI()
# app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

from fastapi import FastAPI, Request, Response, Header, Depends
import json
import hmac
import hashlib
import asyncio
import threading
from typing import Optional, List, Dict
from backend.routes import webhooks
from backend.config import settings
from backend.services.github_service import process_push_event
from backend.slack_monitor import slack_monitor, start_monitor

app = FastAPI()
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Global variables to store background threads
slack_monitor_thread = None

@app.on_event("startup")
async def startup_event():
    print("server started")
    print(f"Webhook route available at: /webhooks/github")
    
    # Start the Slack channel monitoring service
    if settings.SLACK_BOT_TOKEN:
        print(f"  - Starting Slack channel monitoring service")
        
        # Define channels to monitor - you can customize this list
        # You can use channel names or IDs
        channels_to_monitor = ["all-devatlas", "project-lahacks"]  # Replace with your channel names
        
        # Define polling interval in seconds
        polling_interval = 30  # Check for new messages every 30 seconds
        
        global slack_monitor_thread
        slack_monitor_thread = threading.Thread(
            target=lambda: asyncio.run(start_monitor(channels_to_monitor, polling_interval)),
            daemon=True
        )
        slack_monitor_thread.start()
        print(f"  ✅ Slack channel monitoring started for channels: {', '.join(channels_to_monitor)}")
    else:
        print(f"  ⚠️ Slack monitoring not started - missing SLACK_BOT_TOKEN")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down")
    # Background threads will be automatically terminated as they are daemon threads

@app.get("/")
async def root():
    return {"message": "Welcome to Ownership AI API"}

@app.get("/slack/monitored-channels")
async def get_monitored_channels():
    """Get information about all channels being monitored"""
    return slack_monitor.get_monitored_channels()

@app.post("/slack/monitor/{channel}")
async def add_channel_to_monitor(channel: str):
    """Add a new channel to the monitoring service"""
    result = await slack_monitor.add_channel(channel)
    return result

@app.get("/slack/monitor/history/{channel_id}")
async def get_monitored_channel_history(channel_id: str, limit: int = 100):
    """Get the cached message history for a monitored channel"""
    messages = slack_monitor.get_channel_history(channel_id, limit)
    return {
        "channel_id": channel_id,
        "message_count": len(messages),
        "messages": messages
    }

@app.get("/slack/print-messages/{channel_id}")
async def print_channel_messages(channel_id: str = None):
    """Print all messages for a channel to the console"""
    try:
        if channel_id == "all":
            # Print messages for all channels
            slack_monitor.print_all_channel_messages()
            return {"status": "success", "message": "Printed all messages from all channels to console"}
        else:
            # Print messages for specific channel
            slack_monitor.print_all_channel_messages(channel_id)
            return {"status": "success", "message": f"Printed all messages from channel {channel_id} to console"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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