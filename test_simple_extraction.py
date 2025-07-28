#!/usr/bin/env python3
"""
Simple test script to verify JavaScript data extraction
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_products_from_javascript_data(html_content: str, category_name: str):
    """
    Extract products from JavaScript data embedded in the HTML
    """
    products = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for script tags that might contain product data
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            script_content = script.string
            if not script_content:
                continue
            
            # Look for product data patterns in JavaScript
            # Pattern 1: productInfosById object
            product_info_pattern = r'"productInfosById":\s*\{([^}]+)\}'
            product_info_matches = re.findall(product_info_pattern, script_content, re.DOTALL)
            
            for match in product_info_matches:
                # Extract individual product data
                product_pattern = r'"([a-f0-9\-]+)":\s*\{([^}]+)\}'
                product_matches = re.findall(product_pattern, match, re.DOTALL)
                
                for product_id, product_data in product_matches:
                    try:
                        # Extract product information
                        product_name_match = re.search(r'"productName":\s*"([^"]+)"', product_data)
                        title_match = re.search(r'"title":\s*"([^"]+)"', product_data)
                        sku_match = re.search(r'"sku":\s*"([^"]+)"', product_data)
                        
                        # Extract pricing information
                        pricing_pattern = r'"pricing":\s*\{([^}]+)\}'
                        pricing_match = re.search(pricing_pattern, product_data, re.DOTALL)
                        
                        price = None
                        if pricing_match:
                            price_match = re.search(r'"unitListPrice":\s*([\d\.]+)', pricing_match.group(1))
                            if price_match:
                                price = float(price_match.group(1))
                        
                        # Create product data
                        if product_name_match or title_match:
                            product_name = product_name_match.group(1) if product_name_match else title_match.group(1)
                            sku = sku_match.group(1) if sku_match else product_name
                            
                            product_info = {
                                'sku': sku,
                                'product_name': product_name,
                                'description': title_match.group(1) if title_match else product_name,
                                'price': price,
                                'category': category_name
                            }
                            
                            products.append(product_info)
                            print(f"✅ Extracted product: {product_name} (SKU: {sku}, Price: ${price})")
                    
                    except Exception as e:
                        print(f"❌ Error parsing individual product data: {e}")
                        continue
            
            # Pattern 2: Look for product data in other JavaScript objects
            # This is a more general pattern for finding product information
            general_product_pattern = r'"productId":\s*"([^"]+)".*?"productName":\s*"([^"]+)".*?"title":\s*"([^"]+)".*?"sku":\s*"([^"]+)"'
            general_matches = re.findall(general_product_pattern, script_content, re.DOTALL)
            
            for product_id, product_name, title, sku in general_matches:
                try:
                    # Extract price if available
                    price_pattern = rf'"productId":\s*"{re.escape(product_id)}".*?"unitListPrice":\s*([\d\.]+)'
                    price_match = re.search(price_pattern, script_content, re.DOTALL)
                    price = float(price_match.group(1)) if price_match else None
                    
                    product_info = {
                        'sku': sku,
                        'product_name': title,  # Use the full title instead of just productName
                        'description': title,
                        'price': price,
                        'category': category_name
                    }
                    
                    products.append(product_info)
                    print(f"✅ Extracted product from general pattern: {title} (SKU: {sku}, Price: ${price})")
                
                except Exception as e:
                    print(f"❌ Error parsing general product pattern: {e}")
                    continue
        
        print(f"📊 Total products extracted: {len(products)}")
        return products
        
    except Exception as e:
        print(f"❌ Error extracting products from JavaScript data: {e}")
        return []

def test_javascript_extraction():
    """Test the JavaScript data extraction"""
    print("🧪 Testing JavaScript Data Extraction")
    print("=" * 50)
    
    # Read the saved HTML file from our Selenium test
    html_file = Path("debug_selenium_wasp-amp-hornet-insecticide-spray-288EWHIK16.html")
    
    if not html_file.exists():
        print("❌ HTML file not found. Please run the Selenium test first.")
        return
    
    print(f"📄 Reading HTML file: {html_file}")
    
    # Parse the HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Test JavaScript extraction
    print("🔍 Testing JavaScript data extraction...")
    products = extract_products_from_javascript_data(html_content, "Adhesives")
    
    if products:
        print("\n📋 Extracted Products Summary:")
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product['product_name']}")
            print(f"     SKU: {product['sku']}")
            print(f"     Price: ${product['price']}" if product['price'] else "     Price: Not available")
            print(f"     Category: {product['category']}")
            print()
    else:
        print("❌ No products extracted")

if __name__ == "__main__":
    test_javascript_extraction() 