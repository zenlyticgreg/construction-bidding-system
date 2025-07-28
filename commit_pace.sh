#!/bin/bash

# Script to commit the entire PACE project to git

echo "PACE Project - Complete Git Commit"
echo "=================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Show current status
echo "Current git status:"
git status --porcelain

echo ""
echo "Adding all project files..."

# Add all files
git add .

# Count staged files
STAGED_COUNT=$(git diff --cached --name-only | wc -l)
echo "✓ Staged $STAGED_COUNT files for commit"

# Get project statistics
PYTHON_FILES=$(find . -name "*.py" -not -path "./venv/*" | wc -l)
TOTAL_LINES=$(find . -name "*.py" -not -path "./venv/*" -exec wc -l {} + | tail -1 | awk '{print $1}')
DIRECTORIES=$(find . -maxdepth 1 -type d -not -name ".*" -not -name "venv" | wc -l)

echo ""
echo "Project Statistics:"
echo "- Python files: $PYTHON_FILES"
echo "- Total lines of code: $TOTAL_LINES"
echo "- Directories: $DIRECTORIES"

echo ""
echo "Creating commit..."

# Create commit with comprehensive message
git commit -m "PACE - Project Analysis & Construction Estimating System

Complete implementation of the PACE construction bidding automation platform.

PROJECT OVERVIEW:
PACE is a comprehensive system for automating construction bidding processes,
specifically designed for CalTrans and other transportation agencies. The system
provides end-to-end automation from project specification analysis to bid
generation and submission.

CORE FEATURES:
- Automated project specification analysis and extraction
- Product catalog management and matching
- Intelligent bid generation and pricing
- Multi-format report generation (PDF, Excel, CSV)
- Web-based user interface with real-time progress tracking
- Comprehensive data validation and quality assurance
- Integration with CalTrans specifications and requirements

MAJOR COMPONENTS:
1. ANALYZERS: CalTrans specification analyzer, product matching
2. BIDDING ENGINE: Automated bid generation, pricing calculations
3. DATA EXTRACTORS: PDF/online catalog extraction, multi-format support
4. UTILITIES: Data validation, report generation, file processing
5. USER INTERFACE: Web-based dashboard, real-time progress tracking
6. TESTING: Comprehensive unit and integration tests

TECHNICAL SPECIFICATIONS:
- Language: Python 3.8+
- Framework: Custom modular architecture
- UI: Streamlit web interface
- Data: JSON, CSV, Excel, PDF support
- Testing: pytest framework

PROJECT STATISTICS:
- Python files: $PYTHON_FILES
- Total lines of code: $TOTAL_LINES
- Directories: $DIRECTORIES

DEPLOYMENT:
- Cross-platform support (Windows, macOS, Linux)
- Docker containerization ready
- Automated startup scripts
- Comprehensive logging and monitoring

LICENSE: Proprietary - PACE Development Team
VERSION: 1.0.0
BUILD: $(date)

This commit represents the complete PACE system ready for production deployment
and use in construction bidding automation for transportation agencies."

if [ $? -eq 0 ]; then
    echo "✅ PACE project committed successfully!"
    
    echo ""
    echo "Commit summary:"
    git show --stat --oneline -1
    
    echo ""
    echo "Branch information:"
    git branch -v
    
    echo ""
    echo "Next steps:"
    echo "1. To push to remote repository:"
    echo "   git remote add origin <repository-url>"
    echo "   git push -u origin main"
    echo ""
    echo "2. To create a release tag:"
    echo "   git tag -a v1.0.0 -m 'PACE v1.0.0 - Initial Release'"
    echo "   git push origin v1.0.0"
else
    echo "❌ Commit failed"
    exit 1
fi 