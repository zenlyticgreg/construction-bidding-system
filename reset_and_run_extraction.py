#!/usr/bin/env python3
"""
Script to reset extraction progress and run fresh extraction
"""

import os
import json
from pathlib import Path

def reset_progress():
    """Reset the extraction progress file"""
    progress_file = Path("extraction_progress.json")
    
    if progress_file.exists():
        # Backup the old progress file
        backup_file = Path("extraction_progress_backup.json")
        if backup_file.exists():
            backup_file.unlink()
        
        progress_file.rename(backup_file)
        print(f"✅ Backed up old progress to: {backup_file}")
    
    # Create fresh progress file
    fresh_progress = {
        "extracted_products": [],
        "processed_categories": [],
        "timestamp": "2025-07-27T00:00:00"
    }
    
    with open(progress_file, 'w') as f:
        json.dump(fresh_progress, f, indent=2)
    
    print("✅ Reset extraction progress - all categories will be processed fresh")

def main():
    """Main function"""
    print("🔄 Resetting Whitecap Extraction Progress")
    print("=" * 50)
    
    # Reset progress
    reset_progress()
    
    print("\n🚀 Now running fresh extraction...")
    print("=" * 50)
    
    # Run the extraction
    os.system("python run_whitecap_extraction.py")

if __name__ == "__main__":
    main() 