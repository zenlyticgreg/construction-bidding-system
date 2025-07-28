#!/bin/bash

# PACE Application Stop Script
# Stops the PACE application cleanly

echo "🛑 Stopping PACE Application..."

# Kill Streamlit processes
pkill -f streamlit

# Wait for processes to stop
sleep 2

# Check if any processes are still running
if pgrep -f streamlit > /dev/null; then
    echo "⚠️  Some processes may still be running. You can force stop with: pkill -9 -f streamlit"
else
    echo "✅ PACE Application stopped successfully"
fi 