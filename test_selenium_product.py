#!/usr/bin/env python3
"""
Test script to use Selenium to access Whitecap product pages
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

def test_product_page_with_selenium():
    """Test accessing a product page with Selenium"""
    print("🔍 Testing Whitecap Product Page with Selenium")
    print("=" * 60)
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Add user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Test URLs
        test_urls = [
            "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en/Adhesives-en/Construction-Adhesives-en/wasp-amp-hornet-insecticide-spray-288EWHIK16",
            "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en/Adhesives-en/Construction-Adhesives-en"
        ]
        
        for url in test_urls:
            print(f"\n🔍 Testing URL: {url}")
            print("-" * 40)
            
            driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Wait for content to be present
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print(f"⚠️  Timeout waiting for page to load: {e}")
            
            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save the HTML for inspection
            debug_file = Path(f"debug_selenium_{url.split('/')[-1]}.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"📄 Saved HTML to: {debug_file}")
            
            # Look for product information
            print("\n🔍 Searching for product information...")
            
            # Check for product name
            product_name_selectors = [
                'h1', 'h2', '.product-name', '.product-title', '.title',
                '[data-test-selector*="product"]', '[data-testid*="product"]',
                'span[class*="TypographyStyle"]'
            ]
            
            for selector in product_name_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):
                        text = elem.get_text(strip=True)
                        if text and len(text) > 5:  # Only show meaningful text
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
            
            # Check for any elements with data attributes
            print("\n📊 Searching for elements with data attributes...")
            data_elements = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys() if k))
            if data_elements:
                print(f"✅ Found {len(data_elements)} elements with data attributes")
                # Show first few
                for i, elem in enumerate(data_elements[:5]):
                    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                    print(f"   Element {i+1} data attributes: {data_attrs}")
            
            print(f"\n📄 Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"📄 Page length: {len(page_source)} characters")
            
            # Check if this looks like a product page or category page
            page_text = soup.get_text().lower()
            if 'product' in page_text or '$' in page_text:
                print("✅ Page contains product indicators")
            else:
                print("⚠️  Page doesn't contain obvious product indicators")
            
            time.sleep(2)  # Rate limiting
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_product_page_with_selenium() 