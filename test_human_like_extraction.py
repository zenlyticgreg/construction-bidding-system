#!/usr/bin/env python3
"""
Test script to run Whitecap extraction with human-like behavior
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.extractors.whitecap_online_extractor import OnlineExtractionConfig, WhitecapOnlineExtractor

def test_human_like_extraction():
    """Test the extraction with human-like behavior"""
    print("🧪 Testing Whitecap Extraction with Human-Like Behavior")
    print("=" * 60)
    
    # Configuration for human-like extraction
    config = OnlineExtractionConfig(
        categories_to_extract=["Hand Tools"],  # Test with just one category
        max_products_per_category=20,  # Limit for testing
        min_confidence_score=0.3,
        rate_limit_delay=3.0,
        use_selenium=True,
        headless_browser=False,  # Show browser for human-like appearance
        save_progress=False,  # Don't save progress for testing
        # Human-like behavior settings
        human_like_delays=True,
        min_page_load_delay=2.0,
        max_page_load_delay=5.0,
        min_scroll_delay=0.5,
        max_scroll_delay=2.0,
        min_click_delay=1.0,
        max_click_delay=3.0
    )
    
    print("⚙️  Configuration:")
    print(f"   - Categories: {config.categories_to_extract}")
    print(f"   - Max products per category: {config.max_products_per_category}")
    print(f"   - Use Selenium: {config.use_selenium}")
    print(f"   - Headless browser: {config.headless_browser}")
    print(f"   - Human-like delays: {config.human_like_delays}")
    print(f"   - Page load delay: {config.min_page_load_delay}-{config.max_page_load_delay}s")
    print(f"   - Scroll delay: {config.min_scroll_delay}-{config.max_scroll_delay}s")
    print(f"   - Click delay: {config.min_click_delay}-{config.max_click_delay}s")
    print()
    
    try:
        # Create extractor
        print("🔧 Setting up extractor...")
        extractor = WhitecapOnlineExtractor(config)
        
        # Run extraction
        print("🚀 Starting extraction with human-like behavior...")
        print("   This will take longer but should be more reliable...")
        print()
        
        df = extractor.extract_catalog_data()
        
        print("✅ Extraction completed!")
        print()
        
        # Display results
        print("📊 Extraction Results:")
        print(f"   - Total products extracted: {len(df)}")
        print(f"   - Categories processed: {extractor.stats.get('categories_processed', 0)}")
        print(f"   - Subcategories processed: {extractor.stats.get('subcategories_processed', 0)}")
        print()
        
        if len(df) > 0:
            print("📋 Sample Products:")
            for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
                print(f"  {i}. {row['product_name']}")
                print(f"     SKU: {row['sku']}")
                print(f"     Price: ${row['price']}" if pd.notna(row['price']) else "     Price: Not available")
                print(f"     Category: {row['category']}")
                print()
            
            # Save results
            output_file = "human_like_extraction_results.csv"
            df.to_csv(output_file, index=False)
            print(f"💾 Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import pandas as pd
    test_human_like_extraction() 