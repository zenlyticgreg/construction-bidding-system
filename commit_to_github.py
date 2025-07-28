#!/usr/bin/env python3
"""
Script to commit PACE project to GitHub repository
"""

import subprocess
import sys
from pathlib import Path
import os

def run_command(command, check=True):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def main():
    """Commit PACE project to GitHub"""
    
    print("PACE Project - GitHub Commit")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        return
    
    # Check current status
    print("Checking current git status...")
    status = run_command("git status --porcelain")
    if status:
        print("Files to be committed:")
        print(status)
    else:
        print("No changes detected")
    
    # Add remote repository
    remote_url = "https://github.com/zenlyticgreg/construction-bidding-system.git"
    print(f"\nAdding remote repository: {remote_url}")
    
    # Remove existing remote if it exists
    run_command("git remote remove origin", check=False)
    
    # Add new remote
    result = run_command(f"git remote add origin {remote_url}")
    if result is None:
        print("❌ Failed to add remote repository")
        return
    
    print("✓ Remote repository added")
    
    # Check remote
    remotes = run_command("git remote -v")
    print(f"Remote repositories:\n{remotes}")
    
    # Add all files
    print("\nAdding all project files...")
    run_command("git add .")
    print("✓ All files staged")
    
    # Get project statistics
    python_files = len(list(Path('.').rglob('*.py')))
    total_lines = sum(len(open(f, 'r').readlines()) for f in Path('.').rglob('*.py'))
    
    print(f"\nProject Statistics:")
    print(f"- Python files: {python_files}")
    print(f"- Total lines of code: {total_lines:,}")
    
    # Create commit
    print("\nCreating commit...")
    
    commit_message = f"""PACE - Project Analysis & Construction Estimating System

Complete implementation of the PACE construction bidding automation platform.

PROJECT OVERVIEW:
PACE is a comprehensive system for automating construction bidding processes,
specifically designed for CalTrans and other transportation agencies. The system
provides end-to-end automation from project specification analysis to bid
generation and submission.

CORE FEATURES:
- Automated project specification analysis and extraction
- Product catalog management and matching (Whitecap integration)
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
- Python files: {python_files}
- Total lines of code: {total_lines:,}

NEW FEATURES IN THIS COMMIT:
- Whitecap online catalog extractor
- Enhanced PDF processing capabilities
- Improved bid generation algorithms
- Better error handling and validation
- Comprehensive logging and monitoring
- Cross-platform deployment scripts

DEPLOYMENT:
- Cross-platform support (Windows, macOS, Linux)
- Docker containerization ready
- Automated startup scripts
- Comprehensive logging and monitoring

LICENSE: Proprietary - PACE Development Team
VERSION: 1.0.0

This commit represents the complete PACE system ready for production deployment
and use in construction bidding automation for transportation agencies."""
    
    result = run_command(f'git commit -m "{commit_message}"')
    
    if result:
        print("✅ Commit created successfully!")
        print(f"Commit hash: {result}")
        
        # Push to GitHub
        print("\nPushing to GitHub...")
        push_result = run_command("git push -u origin main")
        
        if push_result is not None:
            print("✅ Successfully pushed to GitHub!")
            print(f"Repository: {remote_url}")
            
            print("\n🎉 PACE project successfully committed to GitHub!")
            print("\nNext steps:")
            print("1. View your repository: https://github.com/zenlyticgreg/construction-bidding-system")
            print("2. Create a release tag:")
            print("   git tag -a v1.0.0 -m 'PACE v1.0.0 - Initial Release'")
            print("   git push origin v1.0.0")
            print("3. Set up GitHub Pages or documentation")
            
        else:
            print("❌ Failed to push to GitHub")
            print("You may need to authenticate with GitHub")
            print("Try: git push -u origin main")
            
    else:
        print("❌ Failed to create commit")

if __name__ == "__main__":
    main() 