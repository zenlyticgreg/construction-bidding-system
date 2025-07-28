"""
Script to extract the entire Whitecap online catalog

This script will scrape all product categories and subcategories from whitecap.com
and create a comprehensive catalog file for the bidding system.

Usage:
    python examples/extract_full_whitecap_catalog.py
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.extractors.whitecap_online_extractor import (
        WhitecapOnlineExtractor,
        OnlineExtractionConfig,
        ProductCategory
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def main():
    """Extract the entire Whitecap catalog"""
    
    print("Whitecap Full Catalog Extractor")
    print("=" * 50)
    print("This will extract the entire Whitecap online catalog.")
    print("This process may take several hours depending on the catalog size.")
    print()
    
    # Configuration for full catalog extraction
    config = OnlineExtractionConfig(
        categories_to_extract=[],  # Empty means all categories
        max_products_per_category=5000,  # High limit for full catalog
        min_confidence_score=0.3,  # Lower threshold to capture more products
        rate_limit_delay=2.0,  # Respectful delay
        use_selenium=True,
        headless_browser=True,
        enable_progress_tracking=True,
        save_progress=True,
        progress_file="whitecap_extraction_progress.json"
    )
    
    # Create extractor
    extractor = WhitecapOnlineExtractor(config)
    
    try:
        print("Starting full catalog extraction...")
        print(f"Max products per category: {config.max_products_per_category}")
        print(f"Rate limit delay: {config.rate_limit_delay} seconds")
        print(f"Progress saving: {'Enabled' if config.save_progress else 'Disabled'}")
        print()
        
        start_time = datetime.now()
        
        # Extract catalog data
        df = extractor.extract_catalog_data()
        
        end_time = datetime.now()
        extraction_duration = end_time - start_time
        
        if df.empty:
            print("No products were extracted.")
            return
        
        print(f"Successfully extracted {len(df)} products!")
        print(f"Extraction duration: {extraction_duration}")
        print()
        
        # Display summary
        print("Extraction Summary:")
        print("-" * 30)
        print(f"Total products: {len(df)}")
        print(f"Categories found: {df['category'].nunique()}")
        print(f"Products with prices: {df['price'].notna().sum()}")
        print(f"Average confidence score: {df['confidence_score'].mean():.2f}")
        print()
        
        # Category breakdown
        print("Products by Category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.head(10).items():
            print(f"- {category}: {count} products")
        
        if len(category_counts) > 10:
            print(f"- ... and {len(category_counts) - 10} more categories")
        print()
        
        # Export to CSV
        output_dir = Path("output/catalogs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"whitecap_full_catalog_{timestamp}.csv"
        
        extractor.export_to_csv(df, output_file)
        print(f"Full catalog exported to: {output_file}")
        
        # Create additional exports
        create_category_exports(df, output_dir, timestamp)
        
        # Display statistics
        stats = extractor.get_extraction_stats()
        print()
        print("Detailed Statistics:")
        print(f"- Categories processed: {stats['categories_processed']}")
        print(f"- Errors encountered: {stats['errors']}")
        print(f"- Extraction time: {stats['end_time'] - stats['start_time']}")
        
        # Data quality analysis
        analyze_data_quality(df)
        
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user.")
        print("Progress has been saved. You can resume later.")
    except Exception as e:
        print(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()


def create_category_exports(df: pd.DataFrame, output_dir: Path, timestamp: str):
    """Create separate CSV files for each category"""
    
    print("\nCreating category-specific exports...")
    
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        category_name = category.replace(' ', '_').lower()
        
        category_file = output_dir / f"whitecap_{category_name}_{timestamp}.csv"
        category_df.to_csv(category_file, index=False)
        
        print(f"- {category}: {len(category_df)} products -> {category_file.name}")


def analyze_data_quality(df: pd.DataFrame):
    """Analyze the quality of extracted data"""
    
    print("\nData Quality Analysis:")
    print("=" * 30)
    
    # Missing data analysis
    missing_data = {}
    for column in df.columns:
        missing_count = df[column].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        missing_data[column] = (missing_count, missing_pct)
    
    print("Missing Data:")
    for column, (count, pct) in missing_data.items():
        if count > 0:
            print(f"- {column}: {count} missing ({pct:.1f}%)")
    
    # Price analysis
    if 'price' in df.columns:
        price_stats = df['price'].describe()
        print(f"\nPrice Statistics:")
        print(f"- Mean: ${price_stats['mean']:.2f}")
        print(f"- Median: ${price_stats['50%']:.2f}")
        print(f"- Min: ${price_stats['min']:.2f}")
        print(f"- Max: ${price_stats['max']:.2f}")
        print(f"- Products with prices: {df['price'].notna().sum()} ({df['price'].notna().sum()/len(df)*100:.1f}%)")
    
    # Confidence score distribution
    print(f"\nConfidence Score Distribution:")
    confidence_ranges = [
        (0.9, 1.0, "High (0.9-1.0)"),
        (0.7, 0.9, "Medium (0.7-0.9)"),
        (0.5, 0.7, "Low (0.5-0.7)"),
        (0.3, 0.5, "Very Low (0.3-0.5)"),
        (0.0, 0.3, "Poor (0.0-0.3)")
    ]
    
    for min_score, max_score, label in confidence_ranges:
        count = len(df[(df['c 