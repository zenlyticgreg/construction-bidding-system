#!/bin/bash

# PACE - Project Analysis & Construction Estimating - Run Script

echo "📊  Starting PACE - Project Analysis & Construction Estimating..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is not supported. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads
mkdir -p data/temp
mkdir -p data/backups
mkdir -p data/cache
mkdir -p logs
mkdir -p output/catalogs
mkdir -p output/bids
mkdir -p output/reports
mkdir -p output/analyses

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found"
    exit 1
fi

# Start the application
echo "🚀 Starting PACE application..."
echo "📊 Application will be available at: http://localhost:8501"
echo "🔄 Press Ctrl+C to stop the application"
echo ""

streamlit run main.py --server.port 8501 --server.address localhost 