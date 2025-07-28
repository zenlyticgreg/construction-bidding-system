#!/usr/bin/env python3
"""
Simple script to run the Whitecap online catalog extraction
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'selenium',
        'lxml',
        'webdriver-manager',
        'fake-useragent'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - MISSING")
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies"""
    if packages:
        print(f"\nInstalling missing packages: {', '.join(packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    return True

def run_extraction():
    """Run the Whitecap catalog extraction"""
    print("\nStarting Whitecap catalog extraction...")
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from src.extractors.whitecap_online_extractor import (
            WhitecapOnlineExtractor,
            OnlineExtractionConfig
        )
        
        # Configuration for extraction
        config = OnlineExtractionConfig(
            categories_to_extract=[],  # All categories
            max_products_per_category=1000,
            min_confidence_score=0.3,
            rate_limit_delay=2.0,
            use_selenium=True,  # Use Selenium for dynamic content
            headless_browser=True,
            enable_progress_tracking=True,
            save_progress=True
        )
        
        # Create extractor and run
        extractor = WhitecapOnlineExtractor(config)
        df = extractor.extract_catalog_data()
        
        if not df.empty:
            # Export results
            output_dir = Path("output/catalogs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"whitecap_full_catalog_{timestamp}.csv"
            
            extractor.export_to_csv(df, output_file)
            
            print(f"\n✅ Extraction completed successfully!")
            print(f"📊 Total products extracted: {len(df)}")
            print(f"📁 Output file: {output_file}")
            
            # Show sample data
            print(f"\n📋 Sample products:")
            for idx, row in df.head(3).iterrows():
                print(f"  - {row['product_name']} (SKU: {row['sku']}) - ${row['price'] if row['price'] else 'N/A'}")
                
        else:
            print("❌ No products were extracted")
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("Whitecap Online Catalog Extractor")
    print("=" * 40)
    
    # Check dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\nMissing dependencies detected: {', '.join(missing)}")
        install = input("Install missing dependencies? (y/n): ").lower().strip()
        
        if install == 'y':
            if not install_dependencies(missing):
                print("Failed to install dependencies. Please install manually:")
                print(f"pip install {' '.join(missing)}")
                return
        else:
            print("Cannot proceed without required dependencies.")
            return
    
    # Run extraction
    run_extraction()

if __name__ == "__main__":
    main() 