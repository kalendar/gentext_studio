# Run UV sync
uv sync --extra dev | Out-Null

# Activate virtual environment
.\.venv\Scripts\activate | Out-Null

# Check for pre-commit hook
if (-not (Test-Path -Path ".git\hooks\pre-commit")) {
    pre-commit install
}

# Start tailwindcss in background
Start-Process -NoNewWindow -FilePath "cmd" -ArgumentList "/c npx tailwindcss -i .\src\treebeard\static\css\src\input.css -o .\src\treebeard\static\css\main.css -w"

# Start FastAPI server
fastapi dev .\src\treebeard --port 5080
