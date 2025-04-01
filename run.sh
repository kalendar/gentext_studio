#!/bin/bash

# Run UV sync
uv sync

# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
fastapi run ./src/treebeard --port 5080
