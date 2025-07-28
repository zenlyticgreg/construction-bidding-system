#!/usr/bin/env python3
"""
Debug script to inspect Whitecap product page structure
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

def inspect_product_page(url):
    """Inspect the HTML structure of a Whitecap product page"""
    print(f"🔍 Inspecting product page: {url}")
    print("=" * 60)
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save the HTML for inspection
        debug_file = Path("debug_product_page.html")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"📄 Saved HTML to: {debug_file}")
        
        # Look for product information
        print("\n🔍 Searching for product information...")
        
        # Check for product name
        product_name_selectors = [
            'h1', 'h2', '.product-name', '.product-title', '.title',
            '[data-test-selector*="product"]', '[data-testid*="product"]'
        ]
        
        for selector in product_name_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text(strip=True)
                    if text:
                        print(f"   {i+1}. {text[:100]}...")
        
        # Check for price information
        print("\n💰 Searching for price information...")
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*USD',
            r'Price:\s*\$[\d,]+\.?\d*'
        ]
        
        for pattern in price_patterns:
            price_elements = soup.find_all(text=re.compile(pattern))
            if price_elements:
                print(f"✅ Found {len(price_elements)} elements with price pattern: {pattern}")
                for i, elem in enumerate(price_elements[:5]):
                    print(f"   {i+1}. {elem.strip()}")
        
        # Check for SKU/Product ID
        print("\n🏷️  Searching for SKU/Product ID...")
        sku_patterns = [
            r'SKU[:\s]*([A-Z0-9\-_]+)',
            r'Item[:\s]*([A-Z0-9\-_]+)',
            r'Product[:\s]*([A-Z0-9\-_]+)',
            r'([A-Z]{2,}[0-9]{3,})',
            r'([A-Z0-9]{6,})'
        ]
        
        for pattern in sku_patterns:
            sku_elements = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            if sku_elements:
                print(f"✅ Found {len(sku_elements)} elements with SKU pattern: {pattern}")
                for i, elem in enumerate(sku_elements[:5]):
                    print(f"   {i+1}. {elem.strip()}")
        
        # Check for product description
        print("\n📝 Searching for product description...")
        desc_selectors = [
            '.description', '.product-desc', '.item-desc', '.summary',
            '.product-description', '.details', '.specifications'
        ]
        
        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:2]):
                    text = elem.get_text(strip=True)
                    if text:
                        print(f"   {i+1}. {text[:200]}...")
        
        # Check for any elements with data attributes
        print("\n📊 Searching for elements with data attributes...")
        data_elements = soup.find_all(attrs=lambda x: any(k.startswith('data-') for k in x.keys() if k))
        if data_elements:
            print(f"✅ Found {len(data_elements)} elements with data attributes")
            # Show first few
            for i, elem in enumerate(data_elements[:5]):
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                print(f"   Element {i+1} data attributes: {data_attrs}")
        
        print(f"\n📄 Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"📄 Page length: {len(response.text)} characters")
        
    except Exception as e:
        print(f"❌ Error inspecting page: {e}")

def main():
    """Main function"""
    print("🔍 Whitecap Product Page Inspector")
    print("=" * 50)
    
    # Test with the example product URL you provided
    test_urls = [
        "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en/Adhesives-en/Construction-Adhesives-en/wasp-amp-hornet-insecticide-spray-288EWHIK16",
        "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en/Adhesives-en/Construction-Adhesives-en"
    ]
    
    for url in test_urls:
        inspect_product_page(url)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main() 