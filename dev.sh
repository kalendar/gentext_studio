#!/bin/bash

# Run UV sync
uv sync --extra dev

# Activate virtual environment
source .venv/bin/activate

# Check for pre-commit hook
if [ ! -f ".git/hooks/pre-commit" ]; then
    pre-commit install
fi

# Start tailwindcss, can't use same terminal because fastapi dev kills it on reload.
npx tailwindcss -i ./src/treebeard/static/css/src/input.css -o ./src/treebeard/static/css/main.css -w

# Start FastAPI server
fastapi dev ./src/treebeard --port 5080
