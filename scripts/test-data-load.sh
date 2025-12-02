#!/bin/bash

# Test Data Load Script for Smart City AI Assistant
echo "Loading test data into Smart City AI system..."

# Check if Python agent is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Error: Python agent is not running on port 8000"
    echo "Please start the Python agent first: cd python-agent && python app.py"
    exit 1
fi

echo "✓ Python agent is running"

# Load documents
echo ""
echo "Uploading documents..."

# Upload water supply SOP
echo "  - Uploading water-supply-sop.txt..."
curl -X POST http://localhost:8000/ingest \
  -F "file=@test-data/documents/water-supply-sop.txt" \
  -F 'metadata={"source_name":"Water Supply SOP","uploaded_by":"system","tags":["sop","water"]}' \
  -s | python -m json.tool

# Upload road maintenance SOP
echo "  - Uploading road-maintenance-sop.txt..."
curl -X POST http://localhost:8000/ingest \
  -F "file=@test-data/documents/road-maintenance-sop.txt" \
  -F 'metadata={"source_name":"Road Maintenance SOP","uploaded_by":"system","tags":["sop","roads"]}' \
  -s | python -m json.tool

echo ""
echo "✓ Test data loaded successfully!"
echo ""
echo "You can now:"
echo "  1. Visit http://localhost:3000/chat to ask questions"
echo "  2. Visit http://localhost:3000/map to view complaints"
echo "  3. Visit http://localhost:3000/dashboard to see statistics"
echo ""
echo "Example queries:"
echo '  - "What is the timeline for pothole repairs?"'
echo '  - "Show complaints in Ward 12"'
echo '  - "Water quality testing requirements"'
