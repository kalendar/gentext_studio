#!/bin/bash

# Run UV sync
uv sync --extra dev

# Activate virtual environment
source .venv/bin/activate

# Check for pre-commit hook
if [ ! -f ".git/hooks/pre-commit" ]; then
    pre-commit install
fi

# Start Tailwind CSS in the background
npm ci
npx tailwindcss -i ./src/treebeard/static/css/src/input.css -o ./src/treebeard/static/css/main.css -w &
TAILWIND_PID=$!

# Cleanup function
cleanup() {
    echo "Stopping Tailwind CSS watcher..."
    kill $TAILWIND_PID
}

# Set up trap to clean up on script exit
trap cleanup EXIT

# Start FastAPI server
fastapi dev --port 5080
