# GitHub Webhook uAgents

This directory contains uAgents that process GitHub webhook data and communicate with each other.

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Agents

### 1. GitHub Webhook Agent (`github_webhook_agent.py`)

This agent processes GitHub webhook events and sends the processed data to another agent.

- Receives webhook data from the FastAPI route
- Processes the data the same way as `github_processor.py`
- Sends the processed entities to the Processor Agent

### 2. Processor Agent (`processor_agent.py`)

This agent listens for messages from the GitHub Webhook Agent and prints them to the console.

- Receives processed entities from the GitHub Webhook Agent
- Displays the data in a readable format
- Logs the full JSON for reference

## Setup and Running

### Step 1: Start the Processor Agent

```bash
cd backend
python -m agents.processor_agent
```

When the processor agent starts, it will display its address. Copy this address.

### Step 2: Update the GitHub Webhook Agent

Open `agents/github_webhook_agent.py` and update the `RECIPIENT_AGENTS` dictionary with the processor agent's address:

```python
RECIPIENT_AGENTS = {
    "processor": "agent1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Replace with the actual address
}
```

### Step 3: Start the GitHub Webhook Agent

```bash
cd backend
python -m agents.github_webhook_agent
```

### Step 4: Start the FastAPI Server

```bash
cd backend
uvicorn main:app --reload
```

### Step 5: Use the Webhook Endpoint

Configure your GitHub repository to send webhooks to:

```
https://your-server.com/agent-webhooks/github-to-agent
```

## Flow Diagram

```
GitHub -> Webhook -> FastAPI -> GitHub Webhook Agent -> Processor Agent -> Console Output
```

## Testing

You can test the setup without actual GitHub webhooks by:

1. Making HTTP POST requests to the webhook endpoint with sample payloads
2. Using the `/webhooks/github-debug` endpoint for testing without verification
3. Using a tool like ngrok to expose your local server to the internet for real GitHub webhook testing 