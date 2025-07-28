#!/bin/bash

# PACE Application Startup Script
# Starts the enhanced PACE application silently

echo "🚀 Starting PACE Application..."

# Kill any existing Streamlit processes
pkill -f streamlit 2>/dev/null

# Wait a moment for processes to stop
sleep 1

# Start the application
cd ui && source ../venv/bin/activate && streamlit run demo_app.py --server.port 8505 --server.headless true --logger.level warning > /dev/null 2>&1 &

# Wait for app to start
sleep 3

# Check if app is running
if curl -s http://localhost:8505 > /dev/null; then
    echo "✅ PACE Application is running at: http://localhost:8505"
    echo "📊 Logs are being written to: logs/ui_app.log"
    echo "🔍 To monitor logs: python monitor_logs.py"
else
    echo "❌ Application failed to start. Check logs for errors."
fi 