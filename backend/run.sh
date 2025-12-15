#!/bin/bash

# Backend startup script
echo "Starting Research Paper RAG Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Ollama is running
echo "Checking Ollama connection..."
python3 -c "
import httpx
try:
    response = httpx.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('✓ Ollama is running')
    else:
        print('⚠ Ollama is not responding correctly')
except:
    print('✗ Ollama is not running. Please start Ollama first: ollama serve')
    exit(1)
"

# Check if port 8000 is in use
echo "Checking if port 8000 is available..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 8000 is already in use. Trying to kill existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start FastAPI server
# NOTE: --reload is DISABLED to prevent hot-reload during ML operations
# Hot-reload triggers on filesystem changes (embedding model cache, ChromaDB writes)
# which causes server restarts mid-request and infinite loops
echo "Starting FastAPI server (production mode, no hot-reload)..."
uvicorn app.main:app --port 8000 --host 0.0.0.0

