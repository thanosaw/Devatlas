#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script for reading channel history and thread messages from Slack
"""

import os
import time
import logging
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Slack credentials from environment
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
TEST_CHANNEL = os.getenv("TEST_CHANNEL", "all-devatlas")  # Channel to test in - replace with your test channel

def read_channel_history():
    """Read message history from a channel and thread replies to verify bot permissions"""
    if not SLACK_BOT_TOKEN:
        logger.error("Missing SLACK_BOT_TOKEN environment variable")
        return False
        
    client = WebClient(token=SLACK_BOT_TOKEN)
    
    try:
        # Step 1: Find the channel ID if a name was provided
        channel_id = TEST_CHANNEL
        if not TEST_CHANNEL.startswith("C"):  # Not a channel ID, try to find by name
            logger.info(f"Looking up channel ID for: {TEST_CHANNEL}")
            response = client.conversations_list()
            for channel in response["channels"]:
                if channel["name"] == TEST_CHANNEL:
                    channel_id = channel["id"]
                    break
            logger.info(f"Found channel ID: {channel_id}")
        
        # Step 2: Read message history
        logger.info(f"Reading message history from channel: {channel_id}")
        history = client.conversations_history(channel=channel_id, limit=10)
        
        message_count = len(history["messages"])
        logger.info(f"Successfully retrieved {message_count} messages from channel")
        
        # Print a few messages as examples
        if message_count > 0:
            logger.info("Recent messages:")
            for i, msg in enumerate(history["messages"][:5]):  # Show up to 5 recent messages
                text = msg.get("text", "[No text]")
                user = msg.get("user", "Unknown")
                ts = msg.get("ts", "")
                reply_count = msg.get("reply_count", 0)
                
                logger.info(f"  {i+1}. User {user}: {text[:50]}... [replies: {reply_count}]")
                
                # Step 3: If this message has thread replies, get them
                if reply_count > 0:
                    logger.info(f"  Thread with {reply_count} replies found. Reading thread replies...")
                    try:
                        thread_replies = client.conversations_replies(
                            channel=channel_id,
                            ts=ts,  # Pass the parent message's timestamp
                            limit=10
                        )
                        
                        # Skip the first message as it's the parent
                        for j, reply in enumerate(thread_replies["messages"][1:], 1):
                            reply_text = reply.get("text", "[No text]")
                            reply_user = reply.get("user", "Unknown")
                            logger.info(f"    {j}. Reply from {reply_user}: {reply_text[:40]}...")
                    except SlackApiError as e:
                        logger.error(f"    Error reading thread replies: {e.response['error']}")
        
        return True
        
    except SlackApiError as e:
        logger.error(f"Error reading channel history: {e.response['error']}")
        if e.response['error'] == 'missing_scope':
            logger.error("You need to add the 'channels:history' scope to your Slack app")
            logger.error("Go to https://api.slack.com/apps > Your App > OAuth & Permissions > Bot Token Scopes")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SLACK HISTORY READER")
    print("=" * 50)
    print("\nThis script will:")
    print("1. Connect to your Slack workspace")
    print("2. Find the specified channel")
    print("3. Read recent message history from that channel")
    print("4. Find messages with thread replies and read those threads")
    print("\nRequired scopes for your Slack app:")
    print("- channels:history - To read channel messages and thread replies")
    print("- channels:read - To list and find channels")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    result = read_channel_history()
    
    if result:
        print("\n✅ Completed successfully!")
        print("Your bot can successfully read channel history and thread replies.")
        print("Check the logs above to see the retrieved messages.")
    else:
        print("\n❌ Failed. Check the logs for details.")
        print("You may need to add the 'channels:history' scope to your Slack app.") 