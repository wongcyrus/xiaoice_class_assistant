#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/.."
SYNC_SCRIPT="$BACKEND_DIR/sync_config.py"
VENV_DIR="$SCRIPT_DIR/venv"

# 1. Sync Configuration (generates .env.test and other config files)
echo "Syncing configuration..."
if [ -f "$SYNC_SCRIPT" ]; then
    python3 "$SYNC_SCRIPT"
else
    echo "Error: sync_config.py not found at $SYNC_SCRIPT"
    exit 1
fi

# 2. Setup Virtual Environment
cd "$SCRIPT_DIR" || exit 1
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Install Dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Run Tests
# Note: conftest.py is configured to load environment variables from .env.test
echo "Running tests..."
pytest -v "$@"
