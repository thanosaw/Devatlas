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

from backend.services.github_fetch import fetch_and_save_all_github_data


# Import processing tools
# from backend.processTools.process_all_nodes import main as process_all_nodes
# from backend.processTools.import_to_neo4j import main as import_to_neo4j

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LA Hacks 2025 Webhook Handler")
from fastapi import FastAPI, Request, Response, Header, Depends
import json
import hmac
import hashlib
import asyncio
import threading
from typing import Optional, List, Dict
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import webhooks
from backend.config import settings
from backend.services.github_service import process_push_event
from backend.slack_monitor import slack_monitor, start_monitor
from backend.processTools.rag import query_rag
from backend.processTools.gemini_rag import query_rag as gemini_query_rag

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variables to store background threads
slack_monitor_thread = None

# Add these functions to handle the script execution with proper import paths
def ensure_process_directories():
    """Ensure all necessary directories and files exist for processing"""
    import os
    
    # Create directories if they don't exist
    os.makedirs('backend/processTools', exist_ok=True)
    os.makedirs('processTools', exist_ok=True)
    
    # Define file paths that need to exist
    required_files = {
        'processTools/mock.json': 'processTools/mock.json',
        'processTools/mock.json': None,  # Create empty if doesn't exist
    }
    
    # Create or symlink files
    for target_path, source_path in required_files.items():
        if not os.path.exists(target_path):
            if source_path and os.path.exists(source_path):
                # Create symlink
                print(f"Creating symlink from {source_path} to {target_path}")
                os.symlink(os.path.abspath(source_path), target_path)
            else:
                # Create empty file
                print(f"Creating empty file at {target_path}")
                with open(target_path, 'w') as f:
                    f.write('{"users":[],"repositories":[],"pullRequests":[],"issues":[],"slackChannels":[],"slackMessages":[],"textChunks":[]}')

def run_process_all_nodes():
    """Run the process_all_nodes.py script with proper import handling"""
    import sys
    import os
    
    # Ensure directories and files exist
    ensure_process_directories()
    
    # Add the processTools directory to the Python path
    process_tools_dir = os.path.join(os.path.dirname(__file__), 'processTools')
    if process_tools_dir not in sys.path:
        sys.path.append(process_tools_dir)
    
    # Create mock.json if it doesn't exist
    mock_json_path = os.path.join(process_tools_dir, 'mock.json')
    if not os.path.exists(mock_json_path):
        print(f"Creating empty mock.json file at {mock_json_path}")
        with open(mock_json_path, 'w') as f:
            f.write('{"users":[],"repositories":[],"pullRequests":[],"issues":[],"slackChannels":[],"slackMessages":[],"textChunks":[]}')
    
    # Save original argv
    original_argv = sys.argv.copy()
    
    try:
        # Set clean argv for the script
        sys.argv = [sys.argv[0]]  # Keep just the script name
        print("Running process_all_nodes.py")
        
        # Now import and run the main function
        from process_all_nodes import main
        return main()
    finally:
        # Restore original argv
        sys.argv = original_argv

def run_import_to_neo4j():
    """Run the import_to_neo4j.py script with proper import handling"""
    import sys
    import os
    
    # Add the processTools directory to the Python path
    process_tools_dir = os.path.join(os.path.dirname(__file__), 'processTools')
    if process_tools_dir not in sys.path:
        sys.path.append(process_tools_dir)
    
    # Check for mock_with_embeddings.json
    mock_with_embeddings_path = os.path.join(process_tools_dir, 'mock_with_embeddings.json')
    if not os.path.exists(mock_with_embeddings_path):
        print(f"Warning: {mock_with_embeddings_path} not found. Creating a copy from mock.json")
        mock_json_path = os.path.join(process_tools_dir, 'mock.json')
        if os.path.exists(mock_json_path):
            import shutil
            shutil.copy2(mock_json_path, mock_with_embeddings_path)
        else:
            print(f"Error: mock.json not found either, cannot create mock_with_embeddings.json")
    
    # Save original argv
    original_argv = sys.argv.copy()
    
    try:
        # Set clean argv for the script
        sys.argv = [sys.argv[0]]  # Keep just the script name
        
        # Specify input file explicitly
        print(f"Running import_to_neo4j.py with input file {mock_with_embeddings_path}")
        sys.argv.extend(['--input', mock_with_embeddings_path])
        
        # Now import and run the main function
        from import_to_neo4j import main
        return main()
    finally:
        # Restore original argv
        sys.argv = original_argv

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Server started")
    logger.info(f"Actions file path: actions.json")
    logger.info("Supported webhook events: pull_request, issues, issue_comment, pull_request_review, "
                "pull_request_review_comment, discussion, discussion_comment, label, push")
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
    
    # Process all nodes and import data to Neo4j
    try:
        print("Running process_all_nodes to update embeddings...")
        fetch_and_save_all_github_data("MichaelPeng123", "lahacks2025")
        run_process_all_nodes()
        print("✅ Successfully processed all nodes and added embeddings")
        
        print("Importing data to Neo4j...")
        run_import_to_neo4j()
        print("✅ Successfully imported data to Neo4j")
    except Exception as e:
        print(f"❌ Error during data processing or import: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down")
    # Background threads will be automatically terminated as they are daemon threads

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {"status": "ok", "message": "GitHub webhook handler is running"}


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
    """
    Save all messages for a channel to the JSON file.
    This endpoint was previously used to print messages to console but now writes to a JSON file.
    """
    try:
        if channel_id == "all":
            # Save messages for all channels
            slack_monitor.print_all_channel_messages()
            return {"status": "success", "message": "Saved all messages from all channels to JSON file"}
        else:
            # Save messages for specific channel
            slack_monitor.print_all_channel_messages(channel_id)
            return {"status": "success", "message": f"Saved all messages from channel {channel_id} to JSON file"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/slack/messages-json")
async def get_slack_messages_json():
    """
    Get all Slack messages from the JSON storage file.
    This endpoint is useful for integration with Neo4j and other services.
    """
    try:
        # Get the data using the new method
        message_data = slack_monitor.get_json_message_data()
        
        # Get the file path from the module, not the instance
        from backend.slack_monitor import SLACK_MESSAGES_FILE
        
        return {
            "status": "success",
            "data": message_data,
            "file_path": SLACK_MESSAGES_FILE
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/slack/entities")
async def get_slack_entities():
    """
    Get all Slack data in the new entity format (channels and messages).
    This endpoint returns data in the more normalized format with Channel and Message entities.
    """
    try:
        # Get the entity data
        entity_data = slack_monitor.get_entity_message_data()
        
        # Get the file path from the module
        from backend.slack_monitor import SLACK_ENTITIES_FILE
        
        return {
            "status": "success",
            "data": entity_data,
            "file_path": SLACK_ENTITIES_FILE
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/slack/convert-to-entities")
async def convert_to_entity_format():
    """
    Convert all existing Slack data to the new entity format.
    This endpoint takes the current message data and transforms it into the normalized Channel and Message entities.
    """
    try:
        # Convert the data
        result = slack_monitor.convert_to_entity_format()
        
        return {
            "status": "success",
            "message": f"Successfully converted data to entity format",
            "details": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/slack/update-user-info")
async def update_messages_with_user_info():
    """
    Update all existing messages in the JSON file with user information.
    This converts user IDs to readable usernames and adds profile info.
    """
    try:
        result = slack_monitor.update_existing_messages_with_user_info()
        return {
            "status": result["status"],
            "message": f"Updated {result.get('processed_count', 0)} messages with user info",
            "details": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test-webhook")
async def test_webhook_manually():
    """Test webhook endpoint for manual testing."""
    return {"status": "success", "message": "Test webhook endpoint"}

# Include the webhooks router
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])


@app.get("/slack/thread/{channel_id}/{thread_ts}")
async def get_thread_replies(channel_id: str, thread_ts: str):
    """
    Get all replies in a specific thread.
    
    Args:
        channel_id: The channel ID
        thread_ts: The timestamp of the parent message
        
    Returns:
        Thread replies and parent message
    """
    try:
        # Call the Slack API directly to get fresh thread data
        thread_replies = slack_monitor.client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=100  # Get all replies
        )
        
        messages = thread_replies.get("messages", [])
        
        # Process messages to add user info and convert timestamps
        processed_messages = []
        for msg in messages:
            processed_msg = slack_monitor._process_message_users(msg)
            
            # Convert timestamps to human-readable format
            if "ts" in processed_msg:
                processed_msg["iso_ts"] = slack_monitor._convert_slack_ts_to_iso(processed_msg["ts"])
            if "thread_ts" in processed_msg:
                processed_msg["iso_thread_ts"] = slack_monitor._convert_slack_ts_to_iso(processed_msg["thread_ts"])
                
            processed_messages.append(processed_msg)
        
        # Extract parent message and replies
        parent_message = processed_messages[0] if processed_messages else None
        replies = processed_messages[1:] if len(processed_messages) > 1 else []
        
        return {
            "status": "success",
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "iso_thread_ts": slack_monitor._convert_slack_ts_to_iso(thread_ts),
            "parent_message": parent_message,
            "replies": replies,
            "reply_count": len(replies)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/slack/deduplicate")
async def remove_duplicate_messages():
    """
    Remove duplicate messages from the Slack entities file.
    This endpoint will scan the entities file and remove any duplicate messages based on content.
    """
    try:
        # Get the entity data (this now includes deduplication logic)
        entity_data = slack_monitor.get_entity_message_data()
        
        # Count before and after
        original_count = entity_data.get("original_count", 0)
        current_count = len(entity_data.get("messages", []))
        
        return {
            "status": "success",
            "message": f"Duplicate messages removed successfully",
            "details": {
                "original_message_count": original_count,
                "current_message_count": current_count,
                "duplicates_removed": original_count - current_count if original_count > current_count else 0
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/slack/sort-messages")
async def sort_messages_by_thread():
    """
    Sort all Slack messages first by thread and then chronologically.
    This endpoint organizes messages so that related thread messages are grouped together.
    """
    try:
        # Get the entity data (this will trigger the sort operation)
        entity_data = slack_monitor.get_entity_message_data()
        
        # Get the file path from the module
        from backend.slack_monitor import SLACK_ENTITIES_FILE
        
        return {
            "status": "success",
            "message": "Messages sorted by thread and chronological order",
            "details": {
                "message_count": len(entity_data.get("messages", [])),
                "file_path": SLACK_ENTITIES_FILE
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint_post(chat_query: ChatQuery):
    """
    RAG-powered chat endpoint that answers questions using the knowledge graph (POST method).
    
    Args:
        chat_query: The user's question or query as a JSON body
        
    Returns:
        The answer generated by the RAG system
    """
    try:
        # Extract the query from the request body
        query = chat_query.query
        
        # Capture debug information
        debug_info = {}
        
        # Call the RAG system with the query
        answer, node_type, reason = query_rag(query, top_k=500, capture_debug=debug_info)
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "metadata": {
                "node_type": node_type,
                "reason": reason
            },
            "debug": debug_info
        }
    except Exception as e:
        return {
            "status": "error",
            "query": chat_query.query if hasattr(chat_query, 'query') else "unknown",
            "message": f"Error processing query: {str(e)}"
        }

@app.post("/geminichat")
async def gemini_chat_endpoint_post(chat_query: ChatQuery):
    """
    Gemini-powered RAG chat endpoint that answers questions using the knowledge graph (POST method).
    This endpoint uses Google Gemini instead of AS1 for generating responses.
    
    Args:
        chat_query: The user's question or query as a JSON body
        
    Returns:
        The answer generated by the Gemini RAG system
    """
    try:
        # Extract the query from the request body
        query = chat_query.query
        
        # Capture debug information
        debug_info = {}
        
        # Call the Gemini RAG system with the query
        # Using top_k=15 for better coverage of large datasets
        answer, node_type, reason = gemini_query_rag(query, top_k=500, capture_debug=debug_info)
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "metadata": {
                "node_type": node_type,
                "reason": reason,
                "model": "gemini-2.0-flash"
            },
            "debug": debug_info
        }
    except Exception as e:
        return {
            "status": "error",
            "query": chat_query.query if hasattr(chat_query, 'query') else "unknown",
            "message": f"Error processing query with Gemini: {str(e)}"
        }
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
