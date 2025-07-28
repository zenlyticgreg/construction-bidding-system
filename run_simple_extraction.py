#!/usr/bin/env python3
"""
Simple script to run Whitecap extraction with current setup
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_simple_extraction():
    """Run a simple extraction using the current setup"""
    
    print("Whitecap Catalog Extractor - Simple Mode")
    print("=" * 45)
    
    try:
        from src.extractors.whitecap_online_extractor import (
            WhitecapOnlineExtractor,
            OnlineExtractionConfig
        )
        
        # Simple configuration
        config = OnlineExtractionConfig(
            categories_to_extract=[],
            max_products_per_category=100,
            min_confidence_score=0.3,
            rate_limit_delay=1.0,
            use_selenium=False,  # Start without Selenium
            enable_progress_tracking=True
        )
        
        print("Creating extractor...")
        extractor = WhitecapOnlineExtractor(config)
        
        print("Starting extraction...")
        df = extractor.extract_catalog_data()
        
        if not df.empty:
            # Create output directory
            output_dir = Path("output/catalogs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"whitecap_catalog_{timestamp}.csv"
            
            extractor.export_to_csv(df, output_file)
            
            print(f"\n✅ Extraction completed!")
            print(f"�� Products extracted: {len(df)}")
            print(f"📁 Output file: {output_file}")
            
            # Show summary
            print(f"\n📋 Summary:")
            print(f"  - Categories: {df['category'].nunique()}")
            print(f"  - Products with prices: {df['price'].notna().sum()}")
            print(f"  - Average confidence: {df['confidence_score'].mean():.2f}")
            
            # Show sample products
            print(f"\n📦 Sample products:")
            for idx, row in df.head(5).iterrows():
                print(f"  - {row['product_name']}")
                print(f"    SKU: {row['sku']}, Price: ${row['price'] if pd.notna(row['price']) else 'N/A'}")
                print(f"    Category: {row['category']}")
                print()
                
        else:
            print("❌ No products extracted")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simple_extraction() 