#!/bin/bash

# Script to run Whitecap online catalog extraction

echo "Whitecap Online Catalog Extractor"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install web scraping dependencies
echo "Installing web scraping dependencies..."
pip install -r requirements_web_scraping.txt

# Create output directory
mkdir -p output/catalogs

# Run the extraction
echo "Starting online catalog extraction..."
python examples/whitecap_online_extractor_example.py

echo "Extraction completed!"
echo "Check output/catalogs/ for the extracted data files." 