#!/bin/bash

# PACE UI Demo App Runner
# Runs the enhanced UI demo with file upload fixes

echo "🎨 Starting PACE UI Demo App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if UI directory exists
if [ ! -d "ui" ]; then
    echo "❌ UI directory not found"
    exit 1
fi

# Start the UI demo app
echo "🚀 Starting UI Demo App..."
echo "📊 App will be available at: http://localhost:8505"
echo "🔄 Press Ctrl+C to stop the application"
echo ""

cd ui && streamlit run demo_app.py --server.port 8505 