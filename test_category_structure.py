#!/usr/bin/env python3
"""
Test script to examine the HTML structure of Whitecap category pages
"""

import requests
from bs4 import BeautifulSoup
import re

def test_category_structure():
    """Test the structure of a Whitecap category page"""
    
    # Test URL from the example provided
    test_url = "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en/Adhesives-en"
    
    print(f"Testing URL: {test_url}")
    
    try:
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(test_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Status code: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for potential product containers
        print("\n=== Looking for product containers ===")
        
        # Check for common product selectors
        selectors_to_test = [
            '.product-item',
            '.product-listing',
            '.item',
            '.product-card',
            '.product',
            '[data-product-id]',
            '.catalog-item',
            '.product-container',
            '.item-container'
        ]
        
        for selector in selectors_to_test:
            elements = soup.select(selector)
            print(f"{selector}: {len(elements)} elements found")
            if elements:
                print(f"  First element classes: {elements[0].get('class', [])}")
                print(f"  First element HTML: {str(elements[0])[:200]}...")
        
        # Look for any divs with 'product' in class name
        print("\n=== Divs with 'product' in class name ===")
        product_divs = soup.find_all('div', class_=re.compile(r'product', re.I))
        print(f"Found {len(product_divs)} divs with 'product' in class")
        
        for i, div in enumerate(product_divs[:3]):  # Show first 3
            print(f"  {i+1}. Classes: {div.get('class', [])}")
            print(f"     HTML: {str(div)[:150]}...")
        
        # Look for any elements with 'item' in class name
        print("\n=== Elements with 'item' in class name ===")
        item_elements = soup.find_all(class_=re.compile(r'item', re.I))
        print(f"Found {len(item_elements)} elements with 'item' in class")
        
        for i, elem in enumerate(item_elements[:3]):  # Show first 3
            print(f"  {i+1}. Tag: {elem.name}, Classes: {elem.get('class', [])}")
            print(f"     HTML: {str(elem)[:150]}...")
        
        # Look for any links that might be product links
        print("\n=== Product-like links ===")
        product_links = soup.find_all('a', href=re.compile(r'product|item|sku', re.I))
        print(f"Found {len(product_links)} product-like links")
        
        for i, link in enumerate(product_links[:5]):  # Show first 5
            print(f"  {i+1}. Text: {link.text.strip()}")
            print(f"     Href: {link.get('href')}")
            print(f"     Classes: {link.get('class', [])}")
        
        # Save the HTML for manual inspection
        with open('test_category_page.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"\nFull HTML saved to test_category_page.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_category_structure() 