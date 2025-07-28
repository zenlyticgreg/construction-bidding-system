#!/usr/bin/env python3
"""
Test script to verify the extraction fix
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.extractors.whitecap_online_extractor import (
    WhitecapOnlineExtractor,
    OnlineExtractionConfig
)

def test_extraction():
    """Test the updated extraction logic"""
    print("🧪 Testing Updated Whitecap Extraction")
    print("=" * 50)
    
    # Configuration for testing
    config = OnlineExtractionConfig(
        categories_to_extract=["Hand Tools"],  # Test with just one category
        max_products_per_category=10,  # Limit for testing
        min_confidence_score=0.3,
        rate_limit_delay=1.0,
        use_selenium=True,  # Use Selenium for dynamic content
        headless_browser=True,
        enable_progress_tracking=True,
        save_progress=False  # Don't save progress for testing
    )
    
    # Create extractor and test
    extractor = WhitecapOnlineExtractor(config)
    
    try:
        # Test the full extraction process
        print("📋 Testing full extraction process...")
        df = extractor.extract_catalog_data()
        
        if not df.empty:
            print(f"✅ Successfully extracted {len(df)} products")
            print("\n📋 Sample products:")
            for i, row in df.head(3).iterrows():
                print(f"   {i+1}. {row['product_name']} - ${row['price'] if row['price'] else 'N/A'}")
        else:
            print("❌ No products extracted")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extraction() 