"""
Example script for extracting product data from Whitecap's online catalog

This script demonstrates how to use the WhitecapOnlineExtractor to scrape
product information from whitecap.com and build a catalog product file.

Usage:
    python examples/whitecap_online_extractor_example.py
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.extractors.whitecap_online_extractor import (
        WhitecapOnlineExtractor,
        OnlineExtractionConfig,
        ProductCategory,
        extract_whitecap_online_catalog,
        extract_whitecap_online_categories
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def main():
    """Main function to demonstrate online catalog extraction"""
    
    print("Whitecap Online Catalog Extractor Example")
    print("=" * 50)
    
    # Configuration for extraction
    config = OnlineExtractionConfig(
        categories_to_extract=[
            "adhesives_caulk_sealants",
            "anchoring_fasteners",
            "concrete_forming",
            "safety",
            "tools_equipment"
        ],
        max_products_per_category=50,
        rate_limit_delay=2.0,  # Be respectful with delays
        use_selenium=False,  # Disabled for now
        headless_browser=True,
        enable_progress_tracking=True
    )
    
    # Create extractor
    extractor = WhitecapOnlineExtractor(config)
    
    try:
        print("Starting extraction from Whitecap online catalog...")
        print(f"Target categories: {config.categories_to_extract}")
        print(f"Max products per category: {config.max_products_per_category}")
        print("Note: Currently using sample data. Web scraping will be enabled when dependencies are installed.")
        print()
        
        # Extract catalog data
        df = extractor.extract_catalog_data()
        
        if df.empty:
            print("No products were extracted.")
            return
        
        print(f"Successfully extracted {len(df)} products!")
        print()
        
        # Display sample data
        print("Sample extracted products:")
        print("-" * 30)
        for idx, row in df.head(5).iterrows():
            print(f"SKU: {row['sku']}")
            print(f"Product: {row['product_name']}")
            print(f"Category: {row['category']}")
            print(f"Price: ${row['price'] if pd.notna(row['price']) else 'N/A'}")
            print(f"Confidence: {row['confidence_score']:.2f}")
            print("-" * 30)
        
        # Export to CSV
        output_dir = Path("output/catalogs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"whitecap_online_products_{timestamp}.csv"
        
        extractor.export_to_csv(df, output_file)
        print(f"Data exported to: {output_file}")
        
        # Display statistics
        stats = extractor.get_extraction_stats()
        print()
        print("Extraction Statistics:")
        print(f"- Total products: {stats['total_products']}")
        print(f"- Categories processed: {stats['categories_processed']}")
        print(f"- Errors encountered: {stats['errors']}")
        print(f"- Extraction time: {stats['end_time'] - stats['start_time']}")
        
        # Category breakdown
        print()
        print("Products by Category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"- {category}: {count} products")
        
        # Confidence score distribution
        print()
        print("Confidence Score Distribution:")
        confidence_ranges = [
            (0.9, 1.0, "High (0.9-1.0)"),
            (0.7, 0.9, "Medium (0.7-0.9)"),
            (0.5, 0.7, "Low (0.5-0.7)"),
            (0.0, 0.5, "Very Low (0.0-0.5)")
        ]
        
        for min_score, max_score, label in confidence_ranges:
            count = len(df[(df['confidence_score'] >= min_score) & (df['confidence_score'] < max_score)])
            print(f"- {label}: {count} products")
        
        # Analyze data quality
        analyze_extracted_data(df)
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()


def extract_specific_categories():
    """Example of extracting specific categories only"""
    
    print("\nExtracting specific categories...")
    
    # Extract only safety and concrete forming products
    categories = ["safety", "concrete_forming"]
    
    try:
        df = extract_whitecap_online_categories(categories)
        
        if not df.empty:
            output_file = Path("output/catalogs/whitecap_safety_concrete_products.csv")
            df.to_csv(output_file, index=False)
            print(f"Extracted {len(df)} products from {categories}")
            print(f"Saved to: {output_file}")
        else:
            print("No products extracted from specified categories")
            
    except Exception as e:
        print(f"Category-specific extraction failed: {e}")


def analyze_extracted_data(df: pd.DataFrame):
    """Analyze the extracted data for quality and completeness"""
    
    print("\nData Quality Analysis:")
    print("=" * 30)
    
    # Check for missing data
    missing_data = {}
    for column in df.columns:
        missing_count = df[column].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        missing_data[column] = (missing_count, missing_pct)
    
    print("Missing Data Analysis:")
    for column, (count, pct) in missing_data.items():
        print(f"- {column}: {count} missing ({pct:.1f}%)")
    
    # Price analysis
    if 'price' in df.columns:
        price_stats = df['price'].describe()
        print(f"\nPrice Statistics:")
        print(f"- Mean: ${price_stats['mean']:.2f}")
        print(f"- Median: ${price_stats['50%']:.2f}")
        print(f"- Min: ${price_stats['min']:.2f}")
        print(f"- Max: ${price_stats['max']:.2f}")
    
    # Category distribution
    print(f"\nCategory Distribution:")
    category_dist = df['category'].value_counts()
    for category, count in category_dist.items():
        pct = (count / len(df)) * 100
        print(f"- {category}: {count} products ({pct:.1f}%)")


if __name__ == "__main__":
    main()
    
    # Uncomment to run additional examples
    # extract_specific_categories()