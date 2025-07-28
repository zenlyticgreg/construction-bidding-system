#!/usr/bin/env python3
"""
Debug script to inspect Whitecap's HTML structure
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

def inspect_whitecap_page(url):
    """Inspect the HTML structure of a Whitecap page"""
    print(f"🔍 Inspecting: {url}")
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
        debug_file = Path("debug_whitecap_page.html")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"📄 Saved HTML to: {debug_file}")
        
        # Look for common product-related elements
        print("\n🔍 Searching for product elements...")
        
        # Check for various product selectors
        selectors_to_check = [
            '.product-item', '.product-listing', '.item', '.product-card',
            '.product', '.product-grid', '.product-list',
            '[data-test-selector*="product"]', '[data-testid*="product"]',
            '.catalog-item', '.catalog-product', '.search-result',
            '.product-container', '.product-wrapper'
        ]
        
        for selector in selectors_to_check:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                # Show first element structure
                if elements:
                    print(f"   First element classes: {elements[0].get('class', [])}")
                    print(f"   First element tag: {elements[0].name}")
        
        # Look for price elements
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*USD',
            r'Price:\s*\$[\d,]+\.?\d*'
        ]
        
        print("\n💰 Searching for price elements...")
        for pattern in price_patterns:
            price_elements = soup.find_all(text=re.compile(pattern))
            if price_elements:
                print(f"✅ Found {len(price_elements)} elements with price pattern: {pattern}")
                # Show first few prices
                for i, elem in enumerate(price_elements[:3]):
                    print(f"   Price {i+1}: {elem.strip()}")
        
        # Look for any divs with product-related classes
        print("\n🏷️  Searching for divs with product-related classes...")
        all_divs = soup.find_all('div', class_=True)
        product_divs = []
        
        for div in all_divs:
            classes = div.get('class', [])
            if any('product' in str(c).lower() or 'item' in str(c).lower() or 'card' in str(c).lower() for c in classes):
                product_divs.append(div)
        
        if product_divs:
            print(f"✅ Found {len(product_divs)} divs with product-related classes")
            for i, div in enumerate(product_divs[:5]):
                print(f"   Div {i+1} classes: {div.get('class', [])}")
                # Show some text content
                text = div.get_text(strip=True)[:100]
                if text:
                    print(f"   Text: {text}...")
        else:
            print("❌ No divs with product-related classes found")
        
        # Look for any elements with data attributes
        print("\n📊 Searching for elements with data attributes...")
        data_elements = soup.find_all(attrs=lambda x: any(k.startswith('data-') for k in x.keys() if k))
        if data_elements:
            print(f"✅ Found {len(data_elements)} elements with data attributes")
            # Show first few
            for i, elem in enumerate(data_elements[:5]):
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                print(f"   Element {i+1} data attributes: {data_attrs}")
        
        # Check if it's a React/SPA app
        print("\n⚛️  Checking for React/SPA indicators...")
        react_indicators = [
            'id="root"', 'id="app"', 'data-reactroot',
            'react', 'vue', 'angular', 'spa'
        ]
        
        page_text = soup.get_text().lower()
        for indicator in react_indicators:
            if indicator in page_text or indicator in str(soup):
                print(f"✅ Found React/SPA indicator: {indicator}")
        
        # Check for JavaScript that might load products
        scripts = soup.find_all('script')
        print(f"\n📜 Found {len(scripts)} script tags")
        
        # Look for any API endpoints or product data in scripts
        for script in scripts:
            if script.string:
                script_content = script.string
                if 'product' in script_content.lower() or 'catalog' in script_content.lower():
                    print("✅ Found script with product/catalog references")
                    # Look for URLs or endpoints
                    urls = re.findall(r'https?://[^\s"\'<>]+', script_content)
                    if urls:
                        print(f"   URLs found: {urls[:3]}")
        
        print(f"\n📄 Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"📄 Page length: {len(response.text)} characters")
        
    except Exception as e:
        print(f"❌ Error inspecting page: {e}")

def main():
    """Main function"""
    print("🔍 Whitecap HTML Structure Inspector")
    print("=" * 50)
    
    # Test with a few category URLs
    test_urls = [
        "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en",
        "https://www.whitecap.com/catalog/Hand-Tools-en",
        "https://www.whitecap.com/catalog/Power-Tools-and-Equipment-en"
    ]
    
    for url in test_urls:
        inspect_whitecap_page(url)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main() 