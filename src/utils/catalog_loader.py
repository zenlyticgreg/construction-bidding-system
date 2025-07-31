import pandas as pd
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict, Any

def load_sample_catalog():
    """Load sample catalog for testing and estimation"""
    try:
        # Try to load from JSON file first (current format)
        json_path = Path('pace_sample_catalog.json')
        if json_path.exists():
            with open(json_path, 'r') as f:
                catalog_json = json.load(f)
            
            # Extract products from the JSON structure
            if 'products' in catalog_json:
                catalog_data = catalog_json['products']
                return catalog_data
            else:
                st.error("Invalid catalog format: 'products' key not found")
                return []
        
        # Fallback to CSV if JSON doesn't exist
        csv_path = Path('pace_sample_catalog.csv')
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            catalog_data = df.to_dict('records')
            return catalog_data
        
        st.error("Sample catalog not found. Run catalog_generator.py first.")
        return []
        
    except Exception as e:
        st.error(f"Error loading sample catalog: {str(e)}")
        return []

def display_catalog_summary(catalog_data):
    """Display catalog summary statistics"""
    if not catalog_data:
        return
    
    # Category breakdown
    categories = {}
    total_value = 0
    
    for item in catalog_data:
        cat = item.get('category', 'Unknown')
        price = item.get('price', 0)
        
        if cat not in categories:
            categories[cat] = {'count': 0, 'value': 0}
        categories[cat]['count'] += 1
        categories[cat]['value'] += price
        total_value += price
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", len(catalog_data))
    with col2:
        st.metric("Categories", len(categories))
    with col3:
        if len(catalog_data) > 0:
            avg_price = total_value / len(catalog_data)
            st.metric("Avg Price", f"${avg_price:.2f}")
        else:
            st.metric("Avg Price", "$0.00")
    
    # Category breakdown table
    st.subheader("📊 Catalog by Category")
    category_data = [
        {
            'Category': cat,
            'Items': data['count'],
            'Total Value': f"${data['value']:.2f}",
            'Avg Price': f"${data['value']/data['count']:.2f}" if data['count'] > 0 else "$0.00"
        }
        for cat, data in categories.items()
    ]
    
    st.dataframe(category_data, use_container_width=True)

def convert_catalog_to_dataframe(catalog_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert catalog data to pandas DataFrame for easier manipulation"""
    if not catalog_data:
        return pd.DataFrame()
    
    return pd.DataFrame(catalog_data)

def get_catalog_categories(catalog_data: List[Dict[str, Any]]) -> List[str]:
    """Get unique categories from catalog data"""
    if not catalog_data:
        return []
    
    categories = set()
    for item in catalog_data:
        cat = item.get('category', 'Unknown')
        categories.add(cat)
    
    return sorted(list(categories))

def filter_catalog_by_category(catalog_data: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """Filter catalog data by category"""
    if not catalog_data:
        return []
    
    return [item for item in catalog_data if item.get('category') == category]

def search_catalog(catalog_data: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """Search catalog data by name or SKU"""
    if not catalog_data or not search_term:
        return catalog_data
    
    search_term = search_term.lower()
    results = []
    
    for item in catalog_data:
        name = item.get('name', '').lower()
        sku = item.get('sku', '').lower()
        item_num = item.get('item_num', '').lower()
        
        if (search_term in name or 
            search_term in sku or 
            search_term in item_num):
            results.append(item)
    
    return results 