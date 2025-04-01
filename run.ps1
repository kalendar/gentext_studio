# Run UV sync
uv sync | Out-Null

# Activate virtual environment
.\.venv\Scripts\activate | Out-Null

# Start FastAPI server
fastapi run .\src\treebeard --port 5080
