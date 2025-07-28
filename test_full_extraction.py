#!/usr/bin/env python3
"""
Test script to run the full extraction with updated JavaScript extraction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import only what we need to avoid import issues
from src.extractors.whitecap_online_extractor import OnlineExtractionConfig

def test_extraction():
    """Test the full extraction process"""
    print("🧪 Testing Full Extraction with JavaScript Data Extraction")
    print("=" * 60)
    
    # Configuration for testing
    config = OnlineExtractionConfig(
        categories_to_extract=["Adhesives, Caulk and Sealants"],  # Test with one category
        max_products_per_category=50,  # Limit for testing
        min_confidence_score=0.3,
        rate_limit_delay=2.0,  # Slower for testing
        use_selenium=True,
        headless_browser=True,
        save_progress=False  # Don't save progress for testing
    )
    
    print("⚙️  Configuration:")
    print(f"   - Categories: {config.categories_to_extract}")
    print(f"   - Max products per category: {config.max_products_per_category}")
    print(f"   - Use Selenium: {config.use_selenium}")
    print(f"   - Headless browser: {config.headless_browser}")
    print()
    
    try:
        # Import the extractor here to avoid import issues
        from src.extractors.whitecap_online_extractor import WhitecapOnlineExtractor
        
        # Create extractor
        print("🔧 Setting up extractor...")
        extractor = WhitecapOnlineExtractor(config)
        
        # Run extraction
        print("🚀 Starting extraction...")
        print("   This may take a few minutes...")
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
                print(f"     Confidence: {row['confidence_score']:.2f}")
                print()
            
            # Save results
            output_file = "test_extraction_results.csv"
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
    test_extraction() 