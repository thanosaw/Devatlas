#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to help set up and test the Slack Events API integration.
"""
import requests
import json
import os
from pyngrok import ngrok

# Base URL of your running app
BASE_URL = "http://127.0.0.1:8000"

def setup_ngrok():
    """Set up an ngrok tunnel to expose the local server to the internet."""
    # Start ngrok tunnel to port 8000
    public_url = ngrok.connect(8000).public_url
    print("\n[SUCCESS] Ngrok tunnel established at: %s" % public_url)
    
    # The URL Slack should use for events
    webhook_url = public_url + "/slack/webhook"
    print("[INFO] Use this URL for your Slack Events API Request URL:")
    print("   %s" % webhook_url)
    
    print("\n=== Setup Instructions ===")
    print("1. Go to https://api.slack.com/apps and select your app")
    print("2. Go to 'Event Subscriptions' in the sidebar")
    print("3. Enable Events by toggling the switch to 'On'")
    print("4. Enter the Request URL: %s" % webhook_url)
    print("5. After URL verification succeeds, subscribe to these events:")
    print("   - message.channels (to receive channel messages)")
    print("   - message.groups (for private channels)")
    print("6. Click 'Save Changes' at the bottom of the page")
    print("7. Go to 'OAuth & Permissions' and make sure you have these scopes:")
    print("   - channels:history")
    print("   - groups:history")
    print("   - users:read")
    print("8. Re-install your app to the workspace if needed")
    
    return webhook_url

def test_local_endpoint():
    """Test if the local webhook endpoint is working."""
    print("\n=== Testing Local Endpoint ===")
    
    try:
        # Simple healthcheck
        response = requests.get(BASE_URL + "/")
        if response.status_code == 200:
            print("[SUCCESS] API server is running")
        else:
            print("[ERROR] API server returned status code %d" % response.status_code)
            return False
            
        # Check if webhook endpoint exists (will fail due to signature verification, but that's expected)
        response = requests.post(BASE_URL + "/slack/webhook", json={"test": True})
        if response.status_code == 401:  # Expected to fail with 401 due to missing signature
            print("[SUCCESS] Slack webhook endpoint exists")
        elif response.status_code == 404:
            print("[ERROR] Slack webhook endpoint not found")
            return False
        else:
            print("[WARNING] Unexpected status code from webhook endpoint: %d" % response.status_code)
            
        return True
    
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to the API server. Make sure it's running on port 8000.")
        return False

def environment_check():
    """Check if the environment is properly set up."""
    print("\n=== Environment Check ===")
    
    # Check .env file
    if not os.path.exists(".env"):
        print("[WARNING] No .env file found. Creating a template .env file...")
        with open(".env", "w") as f:
            f.write("GITHUB_WEBHOOK_SECRET=\n")
            f.write("SLACK_BOT_TOKEN=xoxb-your-bot-token-here\n")
            f.write("SLACK_SIGNING_SECRET=your-signing-secret-here\n")
        print("[SUCCESS] Created .env template file. Please fill in your Slack credentials.")
        return False
    
    # Check if token is set
    with open(".env", "r") as f:
        env_content = f.read()
        
    if "SLACK_BOT_TOKEN=xoxb-" not in env_content or "your-bot-token-here" in env_content:
        print("[ERROR] SLACK_BOT_TOKEN not properly set in .env file")
        return False
        
    if "SLACK_SIGNING_SECRET=" not in env_content or "your-signing-secret-here" in env_content:
        print("[ERROR] SLACK_SIGNING_SECRET not properly set in .env file")
        return False
    
    print("[SUCCESS] Environment appears to be properly configured")
    return True

if __name__ == "__main__":
    print("=== Slack Events API Setup Tool ===")
    
    if not environment_check():
        print("\n[WARNING] Please fix the environment issues before continuing.")
        print("   Then restart the server and run this script again.")
        exit(1)
    
    if not test_local_endpoint():
        print("\n[WARNING] Please make sure your server is running properly before continuing.")
        print("   Run it with: PYTHONPATH=/path/to/project python -m uvicorn main:app --reload")
        exit(1)
    
    try:
        webhook_url = setup_ngrok()
        print("\n[SUCCESS] Setup completed!")
        print("   Keep this script running to maintain the ngrok tunnel.")
        print("   Press Ctrl+C to stop the tunnel when you're done.")
        
        # Keep the script running to maintain the ngrok tunnel
        try:
            input("\nPress Enter to exit...\n")
        except KeyboardInterrupt:
            pass
    
    except Exception as e:
        print("\n[ERROR] Error during setup: %s" % str(e))
        print("   Make sure you have ngrok installed and configured properly.")
        
    finally:
        # Clean up ngrok tunnels
        print("\n[INFO] Shutting down ngrok tunnels...")
        ngrok.kill() 