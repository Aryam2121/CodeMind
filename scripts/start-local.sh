#!/bin/bash

# Start local development environment
echo "Starting Smart City AI Assistant..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Error: Node.js is required but not installed."; exit 1; }
command -v python >/dev/null 2>&1 || { echo "Error: Python is required but not installed."; exit 1; }

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OPENAI_API_KEY or set USE_MOCK_LLM=true"
    exit 1
fi

# Start Python agent in background
echo "Starting Python agent..."
cd python-agent
python app.py &
PYTHON_PID=$!
cd ..

# Wait for Python agent to start
echo "Waiting for Python agent to initialize..."
sleep 5

# Start Next.js frontend
echo "Starting Next.js frontend..."
cd frontend
npm run dev &
NEXT_PID=$!
cd ..

echo ""
echo "✓ Services started!"
echo "  - Frontend: http://localhost:3000"
echo "  - Python Agent: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and cleanup
trap "echo 'Stopping services...'; kill $PYTHON_PID $NEXT_PID 2>/dev/null; exit" INT

# Wait for processes
wait
