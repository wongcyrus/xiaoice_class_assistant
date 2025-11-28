#!/bin/bash
set -e

PYTHON_EXEC="python3.12"

echo "Using $PYTHON_EXEC..."

echo "Cleaning up corrupted requests package..."
rm -rf /opt/conda/lib/python3.12/site-packages/requests*

echo "Installing google-adk (latest) and deps..."
# This will install requests as a dependency
$PYTHON_EXEC -m pip install google-adk fastapi starlette uvicorn

echo "Installation complete."
