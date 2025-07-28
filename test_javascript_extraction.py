#!/usr/bin/env python3
"""
Test script to verify JavaScript data extraction
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
from bs4 import BeautifulSoup

def test_javascript_extraction():
    """Test the JavaScript data extraction"""
    print("🧪 Testing JavaScript Data Extraction")
    print("=" * 50)
    
    # Configuration for testing
    config = OnlineExtractionConfig(
        categories_to_extract=[],  # Empty means all categories
        max_products_per_category=10,
        min_confidence_score=0.3,
        rate_limit_delay=1.0,
        use_selenium=True,
        headless_browser=True,
        save_progress=False
    )
    
    # Create extractor
    extractor = WhitecapOnlineExtractor(config)
    
    # Read the saved HTML file from our Selenium test
    html_file = Path("debug_selenium_wasp-amp-hornet-insecticide-spray-288EWHIK16.html")
    
    if not html_file.exists():
        print("❌ HTML file not found. Please run the Selenium test first.")
        return
    
    print(f"📄 Reading HTML file: {html_file}")
    
    # Parse the HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test JavaScript extraction
    print("🔍 Testing JavaScript data extraction...")
    products = extractor._extract_products_from_javascript_data(soup, "Adhesives")
    
    print(f"✅ Found {len(products)} products from JavaScript data")
    
    if products:
        print("\n📋 Extracted Products:")
        for i, product in enumerate(products[:5], 1):  # Show first 5
            print(f"  {i}. {product.product_name}")
            print(f"     SKU: {product.sku}")
            print(f"     Price: ${product.price}" if product.price else "     Price: Not available")
            print(f"     Description: {product.description[:100]}...")
            print()
    
    # Test the full extraction method
    print("🔍 Testing full extraction method...")
    all_products = extractor._extract_products_from_soup(soup, "Adhesives")
    
    print(f"✅ Found {len(all_products)} products total")
    
    if all_products:
        print("\n📋 All Extracted Products:")
        for i, product in enumerate(all_products[:5], 1):  # Show first 5
            print(f"  {i}. {product.product_name}")
            print(f"     SKU: {product.sku}")
            print(f"     Price: ${product.price}" if product.price else "     Price: Not available")
            print(f"     Category: {product.category.value}")
            print()

if __name__ == "__main__":
    test_javascript_extraction() 