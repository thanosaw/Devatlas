#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Continuous Slack channel monitoring service
This module polls Slack channels for new messages and maintains history
"""

import os
import time
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set
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

class SlackMonitor:
    """Service for continuously monitoring Slack channels"""
    
    def __init__(self):
        """Initialize the Slack monitor with bot token"""
        self.token = os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN environment variable not set")
            
        self.client = WebClient(token=self.token)
        self.monitored_channels = {}  # channel_id -> channel_info
        self.latest_timestamps = {}   # channel_id -> latest_ts
        self.message_cache = {}       # channel_id -> list of messages
        self.threads_seen = set()     # Set of parent_ts values we've processed
        self.running = False
        
    async def add_channel(self, channel_name_or_id: str) -> Dict:
        """
        Start monitoring a channel by name or ID
        
        Args:
            channel_name_or_id: Channel name or ID to monitor
            
        Returns:
            Dict with channel information
        """
        try:
            # Get channel ID if name was provided
            channel_id = channel_name_or_id
            if not channel_name_or_id.startswith("C"):
                # Look up channel ID by name
                logger.info(f"Looking up channel ID for: {channel_name_or_id}")
                response = self.client.conversations_list()
                for channel in response["channels"]:
                    if channel["name"] == channel_name_or_id:
                        channel_id = channel["id"]
                        break
                else:
                    return {"status": "error", "error": f"Channel {channel_name_or_id} not found"}
            
            # Get initial info about the channel
            channel_info = self.client.conversations_info(channel=channel_id)["channel"]
            
            # Store channel in our monitored list
            self.monitored_channels[channel_id] = {
                "id": channel_id,
                "name": channel_info.get("name", "unknown"),
                "added_at": datetime.now().isoformat()
            }
            
            # Get initial history to establish latest timestamp
            history = self.client.conversations_history(channel=channel_id, limit=50)  # Increased limit to get more past messages
            messages = history.get("messages", [])
            
            if messages:
                # Store the latest timestamp we've seen
                self.latest_timestamps[channel_id] = messages[0].get("ts")
                # Cache these messages
                self.message_cache[channel_id] = messages
                
                # Log info about channel
                channel_name = channel_info.get('name')
                logger.info(f"Added channel #{channel_name} ({channel_id}) with {len(messages)} initial messages")
                
                # Print past messages
                print(f"\n===== PAST MESSAGES FROM CHANNEL #{channel_name} =====")
                for msg in messages:
                    user = msg.get('user', 'Unknown')
                    text = msg.get('text', 'No text')
                    ts = msg.get('ts', 'Unknown time')
                    print(f"[{ts}] User: {user}")
                    print(f"Message: {text}")
                    print("-" * 50)
                
                # Process any existing threads
                await self._process_threads(channel_id, messages)
            else:
                self.latest_timestamps[channel_id] = "0"
                self.message_cache[channel_id] = []
                logger.info(f"Added channel #{channel_info.get('name')} ({channel_id}) with no messages")
            
            return {
                "status": "success", 
                "channel": self.monitored_channels[channel_id],
                "message_count": len(messages)
            }
            
        except SlackApiError as e:
            logger.error(f"Error adding channel {channel_name_or_id}: {e.response['error']}")
            return {"status": "error", "error": e.response["error"]}
    
    async def _process_threads(self, channel_id: str, messages: List[Dict]) -> None:
        """
        Process thread replies for a list of messages
        
        Args:
            channel_id: The channel ID
            messages: List of message objects
        """
        for msg in messages:
            # Skip if no replies or already processed
            ts = msg.get("ts")
            reply_count = msg.get("reply_count", 0)
            thread_key = f"{channel_id}:{ts}"
            
            if reply_count > 0 and thread_key not in self.threads_seen:
                try:
                    logger.info(f"Reading {reply_count} thread replies in channel {channel_id}")
                    thread_replies = self.client.conversations_replies(
                        channel=channel_id,
                        ts=ts,
                        limit=100  # Get all replies
                    )
                    
                    # Process thread replies (store, analyze, etc)
                    thread_messages = thread_replies.get("messages", [])
                    
                    # Skip the first message as it's the parent
                    thread_replies = thread_messages[1:] if len(thread_messages) > 1 else []
                    
                    # Mark as processed
                    self.threads_seen.add(thread_key)
                    
                    # Here you would process the thread messages
                    # For example, store them in a database
                    logger.info(f"Processed thread with {len(thread_replies)} replies")
                    
                except SlackApiError as e:
                    logger.error(f"Error processing thread {ts}: {e.response['error']}")
    
    async def check_for_updates(self) -> Dict:
        """
        Check all monitored channels for new messages
        
        Returns:
            Dict with update information
        """
        updates = {"new_messages": {}}
        
        for channel_id in self.monitored_channels:
            try:
                # Get messages newer than what we've seen
                latest_ts = self.latest_timestamps.get(channel_id, "0")
                
                history = self.client.conversations_history(
                    channel=channel_id,
                    limit=50,  # Reasonable limit for new messages
                    oldest=latest_ts  # Get messages newer than what we've seen
                )
                
                messages = history.get("messages", [])
                
                if messages and messages[0].get("ts") != latest_ts:
                    # Update the latest timestamp
                    self.latest_timestamps[channel_id] = messages[0].get("ts")
                    
                    # Filter out messages we've already seen
                    new_messages = [msg for msg in messages if msg.get("ts") != latest_ts]
                    
                    if new_messages:
                        channel_name = self.monitored_channels[channel_id]['name']
                        logger.info(f"Found {len(new_messages)} new messages in #{channel_name}")
                        
                        # Print each message content
                        print(f"\n===== NEW MESSAGES IN CHANNEL #{channel_name} =====")
                        for msg in new_messages:
                            user = msg.get('user', 'Unknown')
                            text = msg.get('text', 'No text')
                            ts = msg.get('ts', 'Unknown time')
                            print(f"[{ts}] User: {user}")
                            print(f"Message: {text}")
                            print("-" * 50)
                        
                        # Add to our message cache (prepend to keep chronological order)
                        self.message_cache[channel_id] = new_messages + self.message_cache[channel_id]
                        
                        # Process any threads in the new messages
                        await self._process_threads(channel_id, new_messages)
                        
                        # Add to updates
                        updates["new_messages"][channel_id] = {
                            "count": len(new_messages),
                            "channel_name": self.monitored_channels[channel_id]["name"],
                            "messages": new_messages
                        }
            
            except SlackApiError as e:
                logger.error(f"Error checking channel {channel_id}: {e.response['error']}")
        
        return updates
    
    async def start_monitoring(self, channels: List[str] = None, interval: int = 60) -> None:
        """
        Start continuous monitoring of specified channels
        
        Args:
            channels: List of channel names or IDs to monitor
            interval: Polling interval in seconds
        """
        self.running = True
        
        # Add initial channels if specified
        if channels:
            for channel in channels:
                await self.add_channel(channel)
        
        logger.info(f"Starting continuous monitoring of {len(self.monitored_channels)} channels")
        
        # Main monitoring loop
        while self.running:
            try:
                # Check for new messages in all channels
                updates = await self.check_for_updates()
                
                # Process updates (this is where you'd add custom logic)
                new_message_count = sum(info["count"] for info in updates["new_messages"].values())
                
                if new_message_count > 0:
                    logger.info(f"Processed {new_message_count} new messages across all channels")
                
                # Wait for the next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(interval)  # Still wait before retrying
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring loop"""
        self.running = False
        logger.info("Stopping Slack channel monitoring")
    
    def get_channel_history(self, channel_id: str, limit: int = 100) -> List[Dict]:
        """
        Get cached message history for a channel
        
        Args:
            channel_id: The channel ID
            limit: Maximum number of messages to return
            
        Returns:
            List of message objects
        """
        if channel_id not in self.message_cache:
            return []
            
        return self.message_cache[channel_id][:limit]
    
    def get_monitored_channels(self) -> Dict:
        """
        Get information about all monitored channels
        
        Returns:
            Dict with channel information
        """
        return {
            cid: {
                "info": info,
                "message_count": len(self.message_cache.get(cid, [])),
                "latest_ts": self.latest_timestamps.get(cid)
            }
            for cid, info in self.monitored_channels.items()
        }
        
    def print_all_channel_messages(self, channel_id: str = None) -> None:
        """
        Print all cached messages for a channel or all channels
        
        Args:
            channel_id: Optional specific channel ID to print, or None for all channels
        """
        if channel_id:
            # Print messages for specific channel
            if channel_id in self.message_cache:
                channel_name = self.monitored_channels[channel_id]['name']
                messages = self.message_cache[channel_id]
                
                print(f"\n===== ALL MESSAGES FROM CHANNEL #{channel_name} ({len(messages)} messages) =====")
                for msg in messages:
                    user = msg.get('user', 'Unknown')
                    text = msg.get('text', 'No text')
                    ts = msg.get('ts', 'Unknown time')
                    print(f"[{ts}] User: {user}")
                    print(f"Message: {text}")
                    print("-" * 50)
            else:
                print(f"No messages found for channel {channel_id}")
        else:
            # Print messages for all channels
            for cid, info in self.monitored_channels.items():
                if cid in self.message_cache:
                    channel_name = info['name']
                    messages = self.message_cache[cid]
                    
                    print(f"\n===== ALL MESSAGES FROM CHANNEL #{channel_name} ({len(messages)} messages) =====")
                    for msg in messages:
                        user = msg.get('user', 'Unknown')
                        text = msg.get('text', 'No text')
                        ts = msg.get('ts', 'Unknown time')
                        print(f"[{ts}] User: {user}")
                        print(f"Message: {text}")
                        print("-" * 50)

# Create a singleton instance
slack_monitor = SlackMonitor()

async def start_monitor(channels: List[str] = None, interval: int = 60) -> None:
    """
    Start the Slack monitor with specified channels
    
    Args:
        channels: List of channel names or IDs to monitor
        interval: Polling interval in seconds
    """
    await slack_monitor.start_monitoring(channels, interval)

# For testing the module directly
if __name__ == "__main__":
    print("=" * 50)
    print("SLACK CHANNEL MONITOR")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python slack_monitor.py <channel_name> [<interval_seconds>]")
        print("Example: python slack_monitor.py general 30")
        sys.exit(1)
    
    channel = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    print(f"Starting monitor for channel #{channel} with {interval}s interval")
    print("Press Ctrl+C to stop")
    
    try:
        # Setup the monitor and channels
        monitor = SlackMonitor()
        asyncio.run(monitor.add_channel(channel))
        
        # Then start monitoring
        asyncio.run(monitor.start_monitoring(interval=interval))
    except KeyboardInterrupt:
        print("\nMonitoring stopped") 