#!/bin/bash
# Start the Linguify Documentation Server

echo "🚀 Starting Linguify Documentation Server..."
echo "📍 Working directory: $(pwd)"

# Use the backend venv Python (since docs project is part of the same ecosystem)
PYTHON_PATH="/mnt/c/Users/louis/WebstormProjects/linguify/backend/venv/bin/python"

# Check if Python path exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python not found at $PYTHON_PATH"
    echo "Please make sure the backend virtual environment is set up correctly"
    exit 1
fi

# Run migrations if needed
echo "🔄 Applying migrations..."
$PYTHON_PATH manage.py migrate

# Start the server
echo "🌐 Starting development server on http://127.0.0.1:8000"
echo "📖 Visit the documentation at http://127.0.0.1:8000"
echo ""
echo "To stop the server, press Ctrl+C"
$PYTHON_PATH manage.py runserver