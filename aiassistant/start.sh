#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the Python interpreter (adjust if your python is elsewhere or you use a virtual env)
PYTHON_EXEC="/bin/python" # Or python3, or full path to venv python

# Start the API
lxterminal --title="API" -e "bash -c '${PYTHON_EXEC} ${SCRIPT_DIR}/api/api.py; exec bash'" &

# Start the Listener
lxterminal --title="Listener" -e "bash -c '${PYTHON_EXEC} ${SCRIPT_DIR}/voice_assistant/listener.py; exec bash'" &

echo "API and Listener starting in new terminal windows."
