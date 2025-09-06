#!/bin/bash

echo "🚀 Starting Info Reeler Server..."
echo "=================================="

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in backend directory"
    exit 1
fi

echo "✅ Found main.py in backend directory"
echo "🌐 Starting server on http://localhost:8000"
echo "📱 Open your browser and go to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start the server
python3 main.py
