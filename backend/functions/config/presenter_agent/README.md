# Presenter Agent - Local Testing Guide

## Running the Agent Interactively

### Option 1: Using ADK CLI (Recommended)

Navigate to the presenter_agent directory and run:

```bash
cd /workspaces/xiaoice_class_assistant/backend/functions/config/presenter_agent
adk run .
```

This will start an interactive session where you can chat with the agent. Type your messages and press Enter. Type `exit` to quit.

**Example queries:**
- "Generate a welcoming message for students arriving to class"
- "Create an encouraging message for students taking a test"
- "Write a goodbye message for the end of class"

### Option 2: Using ADK Web UI

For a web-based interface:

```bash
cd /workspaces/xiaoice_class_assistant/backend/functions/config/presenter_agent
adk web .
```

This will start a web server (usually on port 8000) where you can interact with the agent through a browser.

### Option 3: Using ADK API Server

To run as an API server:

```bash
cd /workspaces/xiaoice_class_assistant/backend/functions/config/presenter_agent
adk api_server .
```

This exposes the agent as a REST API that can be called programmatically.

## Configuration

The agent configuration is in `root_agent.yaml`:
- **Model**: gemini-2.5-flash
- **Purpose**: Generate classroom messages and greetings
- **Behavior**: Warm, friendly, and culturally sensitive

Environment variables are loaded from `.env`:
- `GOOGLE_GENAI_USE_VERTEXAI=1` - Use Vertex AI
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- `GOOGLE_CLOUD_LOCATION` - GCP region (e.g., us-central1)

## Modifying the Agent

Edit `root_agent.yaml` to change:
- Agent name
- Model (e.g., gemini-2.5-flash, gemini-2.0-flash)
- Description
- Instructions/personality
- Add tools or sub-agents

Changes take effect immediately - just restart the agent.

## Testing from Python Code

See `../test_agent.py` for an example of programmatically testing the agent.

## Troubleshooting

**Authentication Issues:**
- Ensure you're authenticated: `gcloud auth application-default login`
- Check your .env file has correct GCP project settings

**Module Not Found:**
- Verify ADK is installed: `adk --version`
- Should show version 1.19.0 or higher

**Agent Not Loading:**
- Check `root_agent.yaml` syntax is valid
- Ensure schema reference is present at the top of the file
