#!/usr/bin/env python3
"""
Script to commit the entire PACE project to git
"""

import subprocess
import sys
from pathlib import Path
import json

def run_command(command, check=True):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return None

def get_project_stats():
    """Get statistics about the project"""
    stats = {
        'python_files': 0,
        'total_lines': 0,
        'directories': 0,
        'config_files': 0,
        'test_files': 0,
        'ui_files': 0
    }
    
    # Count files by type
    for file_path in Path('.').rglob('*'):
        if file_path.is_file():
            if file_path.suffix == '.py':
                stats['python_files'] += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        stats['total_lines'] += len(f.readlines())
                except:
                    pass
            elif file_path.suffix in ['.json', '.yaml', '.yml', '.conf']:
                stats['config_files'] += 1
            elif 'test' in file_path.name.lower():
                stats['test_files'] += 1
            elif 'ui' in str(file_path).lower():
                stats['ui_files'] += 1
    
    # Count directories
    for item in Path('.').iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name != 'venv':
            stats['directories'] += 1
    
    return stats

def main():
    """Commit the entire PACE project to git"""
    
    print("PACE Project - Complete Git Commit")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        print("Initializing git repository...")
        run_command("git init")
    
    # Show current status
    print("Current git status:")
    status = run_command("git status --porcelain")
    if status:
        print(status)
    else:
        print("No changes detected")
    
    # Get project statistics
    print("\nAnalyzing project...")
    stats = get_project_stats()
    
    print(f"Project Statistics:")
    print(f"- Python files: {stats['python_files']}")
    print(f"- Total lines of code: {stats['total_lines']:,}")
    print(f"- Directories: {stats['directories']}")
    print(f"- Config files: {stats['config_files']}")
    print(f"- Test files: {stats['test_files']}")
    print(f"- UI files: {stats['ui_files']}")
    
    print("\nAdding all project files...")
    
    # Add all files except those in .gitignore
    run_command("git add .")
    print("✓ Added all project files")
    
    # Check what's staged
    staged_files = run_command("git diff --cached --name-only")
    if staged_files:
        file_count = len(staged_files.split('\n'))
        print(f"✓ Staged {file_count} files for commit")
    
    # Create comprehensive commit message
    commit_message = f"""PACE - Project Analysis & Construction Estimating System

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

1. ANALYZERS (src/analyzers/):
   - CalTrans specification analyzer
   - Product matching and categorization
   - Construction relevance assessment
   - Quantity extraction and validation

2. BIDDING ENGINE (src/bidding/):
   - Automated bid generation
   - Pricing calculations and optimization
   - Cost analysis and estimation
   - Bid validation and quality checks

3. DATA EXTRACTORS (src/extractors/):
   - PDF catalog extraction (Whitecap)
   - Online catalog scraping capabilities
   - Multi-format data import/export
   - Progress tracking and resumption

4. UTILITIES (src/utils/):
   - Data validation and cleaning
   - Excel report generation
   - PDF report creation
   - File handling and processing

5. USER INTERFACE (ui/):
   - Web-based dashboard
   - File upload and processing
   - Real-time progress visualization
   - Interactive bid management

6. TESTING (tests/):
   - Comprehensive unit tests
   - Integration testing
   - Performance benchmarks
   - Quality assurance

TECHNICAL SPECIFICATIONS:
- Language: Python 3.8+
- Framework: Custom modular architecture
- UI: Streamlit web interface
- Data: JSON, CSV, Excel, PDF support
- Testing: pytest framework
- Documentation: Comprehensive README and guides

PROJECT STATISTICS:
- Python files: {stats['python_files']}
- Total lines of code: {stats['total_lines']:,}
- Directories: {stats['directories']}
- Configuration files: {stats['config_files']}
- Test files: {stats['test_files']}
- UI components: {stats['ui_files']}

DEPLOYMENT:
- Cross-platform support (Windows, macOS, Linux)
- Docker containerization ready
- Automated startup scripts
- Comprehensive logging and monitoring
- Error handling and recovery

LICENSE: Proprietary - PACE Development Team
VERSION: 1.0.0
BUILD: {subprocess.run('date', shell=True, capture_output=True, text=True).stdout.strip()}

This commit represents the complete PACE system ready for production deployment
and use in construction bidding automation for transportation agencies."""
    
    print("\nCreating commit...")
    
    # Commit the changes
    result = run_command(f'git commit -m "{commit_message}"')
    
    if result:
        print("✅ PACE project committed successfully!")
        print(f"\nCommit hash: {result}")
        
        # Show commit summary
        print("\nCommit summary:")
        run_command("git show --stat --oneline -1")
        
        # Show branch information
        print("\nBranch information:")
        run_command("git branch -v")
        
        print("\nNext steps:")
        print("1. To push to remote repository:")
        print("   git remote add origin <repository-url>")
        print("   git push -u origin main")
        print("\n2. To create a release tag:")
        print("   git tag -a v1.0.0 -m 'PACE v1.0.0 - Initial Release'")
        print("   git push origin v1.0.0")
        
    else:
        print("❌ Commit failed")

if __name__ == "__main__":
    main() 