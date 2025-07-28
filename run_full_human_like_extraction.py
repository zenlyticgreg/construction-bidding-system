#!/usr/bin/env python3
"""
Full Whitecap extraction with human-like behavior
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.extractors.whitecap_online_extractor import OnlineExtractionConfig, WhitecapOnlineExtractor

def run_full_extraction():
    """Run the full Whitecap extraction with human-like behavior"""
    print("🚀 Starting Full Whitecap Extraction with Human-Like Behavior")
    print("=" * 70)
    print("This will extract products from all available categories")
    print("The process will take longer due to human-like delays")
    print("=" * 70)
    
    # Configuration for full extraction with human-like behavior
    config = OnlineExtractionConfig(
        categories_to_extract=[],  # Empty means all categories
        max_products_per_category=500,  # Reasonable limit for full extraction
        min_confidence_score=0.3,
        rate_limit_delay=3.0,
        use_selenium=True,
        headless_browser=False,  # Show browser for human-like appearance
        save_progress=True,  # Save progress for resuming if needed
        progress_file="human_like_extraction_progress.json",
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
    print(f"   - Categories: All available categories")
    print(f"   - Max products per category: {config.max_products_per_category}")
    print(f"   - Use Selenium: {config.use_selenium}")
    print(f"   - Headless browser: {config.headless_browser}")
    print(f"   - Human-like delays: {config.human_like_delays}")
    print(f"   - Page load delay: {config.min_page_load_delay}-{config.max_page_load_delay}s")
    print(f"   - Scroll delay: {config.min_scroll_delay}-{config.max_scroll_delay}s")
    print(f"   - Click delay: {config.min_click_delay}-{config.max_click_delay}s")
    print(f"   - Save progress: {config.save_progress}")
    print()
    
    try:
        # Create extractor
        print("🔧 Setting up extractor...")
        extractor = WhitecapOnlineExtractor(config)
        
        # Run extraction
        print("🚀 Starting full extraction...")
        print("   This may take 30-60 minutes depending on the number of categories")
        print("   You can see the browser window and human-like behavior")
        print("   Progress will be saved automatically")
        print()
        
        df = extractor.extract_catalog_data()
        
        print("✅ Full extraction completed!")
        print()
        
        # Display comprehensive results
        print("📊 Extraction Results:")
        print(f"   - Total products extracted: {len(df)}")
        print(f"   - Categories processed: {extractor.stats.get('categories_processed', 0)}")
        print(f"   - Subcategories processed: {extractor.stats.get('subcategories_processed', 0)}")
        print(f"   - Errors encountered: {extractor.stats.get('errors', 0)}")
        
        if 'start_time' in extractor.stats and 'end_time' in extractor.stats:
            duration = extractor.stats['end_time'] - extractor.stats['start_time']
            print(f"   - Total duration: {duration}")
        
        print()
        
        if len(df) > 0:
            print("📋 Sample Products:")
            for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
                print(f"  {i:2d}. {row['product_name'][:60]}...")
                print(f"      SKU: {row['sku']}")
                print(f"      Price: ${row['price']:.2f}" if pd.notna(row['price']) else "      Price: Not available")
                print(f"      Category: {row['category']}")
                print(f"      Subcategory: {row['subcategory']}")
                print()
            
            # Save results
            output_file = "full_whitecap_extraction_results.csv"
            df.to_csv(output_file, index=False)
            print(f"💾 Full results saved to: {output_file}")
            
            # Also save a summary
            summary_file = "extraction_summary.txt"
            with open(summary_file, 'w') as f:
                f.write("Whitecap Extraction Summary\n")
                f.write("=" * 30 + "\n")
                f.write(f"Total products: {len(df)}\n")
                f.write(f"Categories processed: {extractor.stats.get('categories_processed', 0)}\n")
                f.write(f"Subcategories processed: {extractor.stats.get('subcategories_processed', 0)}\n")
                f.write(f"Errors: {extractor.stats.get('errors', 0)}\n")
                if 'start_time' in extractor.stats and 'end_time' in extractor.stats:
                    f.write(f"Duration: {duration}\n")
                f.write(f"Output file: {output_file}\n")
            
            print(f"📝 Summary saved to: {summary_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error during full extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import pandas as pd
    run_full_extraction() 