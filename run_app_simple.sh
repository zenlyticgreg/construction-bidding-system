#!/bin/bash

# Simple PACE App Runner (for when environment is already set up)

echo "🚀 Starting PACE Application..."

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "📊 Application will be available at: http://localhost:8501"
echo "🔄 Press Ctrl+C to stop the application"
echo ""

streamlit run main.py --server.port 8501 --server.address localhost 