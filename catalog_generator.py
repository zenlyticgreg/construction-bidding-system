#!/usr/bin/env python3
"""
PACE Construction Products Catalog Generator
Creates comprehensive sample catalog for construction project estimation
"""

import pandas as pd
import json
from datetime import datetime

def create_construction_catalog():
    """Generate comprehensive construction products catalog"""
    
    catalog_data = []
    
    # CATEGORY 1: CONCRETE & MASONRY
    concrete_products = [
        {"category": "Concrete", "item_num": "C001", "name": "Concrete - Ready-Mix 3000 PSI", "sku": "RMC-3000", "unit": "CY", "price": 145.00},
        {"category": "Concrete", "item_num": "C002", "name": "Concrete - Ready-Mix 4000 PSI", "sku": "RMC-4000", "unit": "CY", "price": 165.00},
        {"category": "Concrete", "item_num": "C003", "name": "Concrete - Ready-Mix 5000 PSI Bridge Grade", "sku": "RMC-5000", "unit": "CY", "price": 185.00},
        {"category": "Concrete", "item_num": "C004", "name": "Concrete - Fiber Reinforced 4000 PSI", "sku": "FRC-4000", "unit": "CY", "price": 195.00},
        {"category": "Concrete", "item_num": "C005", "name": "Concrete - Lightweight Structural", "sku": "LWC-3000", "unit": "CY", "price": 175.00},
        {"category": "Concrete", "item_num": "C006", "name": "Concrete - Self-Consolidating", "sku": "SCC-4000", "unit": "CY", "price": 225.00},
        {"category": "Concrete", "item_num": "C007", "name": "Concrete - Accelerator Admixture", "sku": "ADM-ACC", "unit": "GAL", "price": 45.00},
        {"category": "Concrete", "item_num": "C008", "name": "Concrete - Retarding Admixture", "sku": "ADM-RET", "unit": "GAL", "price": 42.00},
        {"category": "Concrete", "item_num": "C009", "name": "Concrete - Penetrating Sealer", "sku": "CS-PEN", "unit": "GAL", "price": 38.50},
        {"category": "Concrete", "item_num": "C010", "name": "Concrete - Curing Compound", "sku": "CC-WAX", "unit": "GAL", "price": 28.75},
        {"category": "Masonry", "item_num": "C011", "name": "Masonry - Concrete Block 8x8x16", "sku": "CMU-8816", "unit": "EA", "price": 3.25},
        {"category": "Masonry", "item_num": "C012", "name": "Masonry - Concrete Block 12x8x16", "sku": "CMU-12816", "unit": "EA", "price": 4.85},
        {"category": "Masonry", "item_num": "C013", "name": "Masonry - Type S Mortar Mix", "sku": "MOR-S", "unit": "BAG", "price": 8.95},
        {"category": "Masonry", "item_num": "C014", "name": "Masonry - Fine Grout", "sku": "GRT-FINE", "unit": "BAG", "price": 12.50},
        {"category": "Concrete", "item_num": "C015", "name": "Concrete - Expansion Joint Filler 1/2\"", "sku": "EJF-1/2", "unit": "LF", "price": 4.25},
    ]
    
    # CATEGORY 2: LUMBER & WOOD PRODUCTS  
    lumber_products = [
        {"category": "Lumber", "item_num": "L001", "name": "Lumber - 2x4x8 Douglas Fir", "sku": "DF-2X4X8", "unit": "EA", "price": 8.95},
        {"category": "Lumber", "item_num": "L002", "name": "Lumber - 2x4x10 Douglas Fir", "sku": "DF-2X4X10", "unit": "EA", "price": 12.25},
        {"category": "Lumber", "item_num": "L003", "name": "Lumber - 2x4x12 Douglas Fir", "sku": "DF-2X4X12", "unit": "EA", "price": 14.75},
        {"category": "Lumber", "item_num": "L004", "name": "Lumber - 2x6x8 Douglas Fir", "sku": "DF-2X6X8", "unit": "EA", "price": 13.50},
        {"category": "Lumber", "item_num": "L005", "name": "Lumber - 2x6x10 Douglas Fir", "sku": "DF-2X6X10", "unit": "EA", "price": 16.85},
        {"category": "Lumber", "item_num": "L006", "name": "Lumber - 2x6x12 Douglas Fir", "sku": "DF-2X6X12", "unit": "EA", "price": 20.25},
        {"category": "Lumber", "item_num": "L007", "name": "Lumber - 2x8x10 Douglas Fir", "sku": "DF-2X8X10", "unit": "EA", "price": 22.50},
        {"category": "Lumber", "item_num": "L008", "name": "Lumber - 2x8x12 Douglas Fir", "sku": "DF-2X8X12", "unit": "EA", "price": 27.00},
        {"category": "Lumber", "item_num": "L009", "name": "Lumber - 2x10x12 Douglas Fir", "sku": "DF-2X10X12", "unit": "EA", "price": 33.75},
        {"category": "Lumber", "item_num": "L010", "name": "Lumber - 2x12x12 Douglas Fir", "sku": "DF-2X12X12", "unit": "EA", "price": 40.50},
        {"category": "Lumber", "item_num": "L011", "name": "Lumber - 4x4x8 Pressure Treated", "sku": "PT-4X4X8", "unit": "EA", "price": 18.95},
        {"category": "Lumber", "item_num": "L012", "name": "Lumber - 6x6x8 Pressure Treated", "sku": "PT-6X6X8", "unit": "EA", "price": 42.50},
        {"category": "Lumber", "item_num": "L013", "name": "Lumber - 6x8x12 Heavy Timber", "sku": "HT-6X8X12", "unit": "EA", "price": 89.50},
        {"category": "Lumber", "item_num": "L014", "name": "Lumber - 6x12x16 Heavy Timber", "sku": "HT-6X12X16", "unit": "EA", "price": 156.00},
        {"category": "Lumber", "item_num": "L015", "name": "Lumber - Plywood 3/4\" CDX 4x8", "sku": "PLY-3/4CDX", "unit": "SHT", "price": 48.75},
        {"category": "Lumber", "item_num": "L016", "name": "Lumber - Plywood 5/8\" CDX 4x8", "sku": "PLY-5/8CDX", "unit": "SHT", "price": 42.25},
        {"category": "Lumber", "item_num": "L017", "name": "Lumber - Plywood 1/2\" HDO Form 4x8", "sku": "PLY-1/2HDO", "unit": "SHT", "price": 62.50},
        {"category": "Lumber", "item_num": "L018", "name": "Lumber - OSB 7/16\" 4x8 Sheathing", "sku": "OSB-7/16", "unit": "SHT", "price": 24.95},
    ]
    
    # CATEGORY 3: STRUCTURAL STEEL & REINFORCEMENT
    steel_products = [
        {"category": "Steel", "item_num": "S001", "name": "Steel - W12x26 Wide Flange Beam", "sku": "W12X26", "unit": "LF", "price": 32.50},
        {"category": "Steel", "item_num": "S002", "name": "Steel - W14x30 Wide Flange Beam", "sku": "W14X30", "unit": "LF", "price": 37.50},
        {"category": "Steel", "item_num": "S003", "name": "Steel - W16x36 Wide Flange Beam", "sku": "W16X36", "unit": "LF", "price": 45.00},
        {"category": "Steel", "item_num": "S004", "name": "Steel - W18x40 Wide Flange Beam", "sku": "W18X40", "unit": "LF", "price": 50.00},
        {"category": "Steel", "item_num": "S005", "name": "Steel - W21x50 Wide Flange Beam", "sku": "W21X50", "unit": "LF", "price": 62.50},
        {"category": "Steel", "item_num": "S006", "name": "Steel - HSS8x8x1/2 Column", "sku": "HSS8X8", "unit": "LF", "price": 50.88},
        {"category": "Steel", "item_num": "S007", "name": "Steel - HSS6x6x1/2 Column", "sku": "HSS6X6", "unit": "LF", "price": 39.75},
        {"category": "Steel", "item_num": "S008", "name": "Steel - L4x4x1/2 Angle", "sku": "L4X4", "unit": "LF", "price": 16.00},
        {"category": "Steel", "item_num": "S009", "name": "Steel - L6x6x1/2 Angle", "sku": "L6X6", "unit": "LF", "price": 24.50},
        {"category": "Reinforcement", "item_num": "S010", "name": "Reinforcement - #4 Rebar", "sku": "RB-4", "unit": "LF", "price": 0.95},
        {"category": "Reinforcement", "item_num": "S011", "name": "Reinforcement - #5 Rebar", "sku": "RB-5", "unit": "LF", "price": 1.45},
        {"category": "Reinforcement", "item_num": "S012", "name": "Reinforcement - #6 Rebar", "sku": "RB-6", "unit": "LF", "price": 2.10},
        {"category": "Reinforcement", "item_num": "S013", "name": "Reinforcement - #8 Rebar", "sku": "RB-8", "unit": "LF", "price": 3.75},
        {"category": "Reinforcement", "item_num": "S014", "name": "Reinforcement - Welded Wire Mesh 6x6", "sku": "WWM-6X6", "unit": "SF", "price": 1.25},
        {"category": "Steel", "item_num": "S015", "name": "Steel - Fabrication & Welding", "sku": "FAB-WELD", "unit": "LB", "price": 0.35},
    ]
    
    # CATEGORY 4: FORMWORK & ACCESSORIES
    formwork_products = [
        {"category": "Formwork", "item_num": "F001", "name": "Formwork - Steel Form Ties 1/2\"", "sku": "TIE-1/2", "unit": "EA", "price": 0.85},
        {"category": "Formwork", "item_num": "F002", "name": "Formwork - Steel Form Ties 5/8\"", "sku": "TIE-5/8", "unit": "EA", "price": 1.15},
        {"category": "Formwork", "item_num": "F003", "name": "Formwork - Form Release Agent", "sku": "REL-AGT", "unit": "GAL", "price": 32.50},
        {"category": "Formwork", "item_num": "F004", "name": "Formwork - Steel Waler Clamps", "sku": "WAL-CLAMP", "unit": "EA", "price": 12.50},
        {"category": "Formwork", "item_num": "F005", "name": "Formwork - Form Spreaders", "sku": "SPREAD", "unit": "EA", "price": 8.75},
        {"category": "Formwork", "item_num": "F006", "name": "Formwork - Corner Forms", "sku": "CORNER", "unit": "LF", "price": 15.50},
        {"category": "Formwork", "item_num": "F007", "name": "Formwork - Blockout Forms", "sku": "BLKOUT", "unit": "EA", "price": 25.00},
        {"category": "Formwork", "item_num": "F008", "name": "Formwork - Textured Form Liner", "sku": "TEX-LINER", "unit": "SF", "price": 4.50},
        {"category": "Formwork", "item_num": "F009", "name": "Formwork - Fractured Rib Liner", "sku": "FRAC-RIB", "unit": "SF", "price": 5.25},
        {"category": "Formwork", "item_num": "F010", "name": "Formwork - Steel Edge Forms", "sku": "EDGE-STL", "unit": "LF", "price": 8.95},
        {"category": "Formwork", "item_num": "F011", "name": "Formwork - Aluminum Edge Forms", "sku": "EDGE-ALU", "unit": "LF", "price": 12.50},
        {"category": "Formwork", "item_num": "F012", "name": "Formwork - Form Stripping Tools", "sku": "STRIP-TOOL", "unit": "EA", "price": 45.00},
    ]
    
    # CATEGORY 5: DOORS, WINDOWS & HARDWARE
    openings_products = [
        {"category": "Doors", "item_num": "D001", "name": "Doors - Steel Entry Door 3'x7'", "sku": "STL-DR-37", "unit": "EA", "price": 425.00},
        {"category": "Doors", "item_num": "D002", "name": "Doors - Steel Entry Door 4'x7'", "sku": "STL-DR-47", "unit": "EA", "price": 485.00},
        {"category": "Doors", "item_num": "D003", "name": "Doors - Hollow Metal Frame", "sku": "HM-FRAME", "unit": "EA", "price": 185.00},
        {"category": "Doors", "item_num": "D004", "name": "Doors - Heavy Duty Hinges", "sku": "HD-HINGE", "unit": "SET", "price": 45.50},
        {"category": "Doors", "item_num": "D005", "name": "Doors - Lock Set Commercial", "sku": "LOCK-COM", "unit": "EA", "price": 165.00},
        {"category": "Doors", "item_num": "D006", "name": "Doors - Exit Device", "sku": "EXIT-DEV", "unit": "EA", "price": 285.00},
        {"category": "Windows", "item_num": "W001", "name": "Windows - Aluminum Fixed 3'x4'", "sku": "ALU-FIX-34", "unit": "EA", "price": 285.00},
        {"category": "Windows", "item_num": "W002", "name": "Windows - Aluminum Fixed 4'x6'", "sku": "ALU-FIX-46", "unit": "EA", "price": 425.00},
        {"category": "Windows", "item_num": "W003", "name": "Windows - Aluminum Casement", "sku": "ALU-CASE", "unit": "EA", "price": 385.00},
        {"category": "Windows", "item_num": "W004", "name": "Windows - Glass 1/4\" Tempered", "sku": "GLS-TEMP", "unit": "SF", "price": 12.50},
        {"category": "Hardware", "item_num": "H001", "name": "Hardware - Anchor Bolts 1/2\"x8\"", "sku": "AB-1/2X8", "unit": "EA", "price": 4.25},
        {"category": "Hardware", "item_num": "H002", "name": "Hardware - Anchor Bolts 5/8\"x10\"", "sku": "AB-5/8X10", "unit": "EA", "price": 6.75},
        {"category": "Hardware", "item_num": "H003", "name": "Hardware - Expansion Anchors", "sku": "EXP-ANCH", "unit": "EA", "price": 2.85},
    ]
    
    # CATEGORY 6: BRIDGE & HIGHWAY SPECIALTIES (CalTrans Specific)
    bridge_products = [
        {"category": "Bridge", "item_num": "B001", "name": "Bridge - Baluster Posts Precast", "sku": "BAL-POST", "unit": "EA", "price": 125.00},
        {"category": "Bridge", "item_num": "B002", "name": "Bridge - Baluster Forms Heavy Duty", "sku": "BAL-FORM", "unit": "LF", "price": 25.50},
        {"category": "Bridge", "item_num": "B003", "name": "Bridge - Type 86H Rail System", "sku": "86H-RAIL", "unit": "LF", "price": 185.00},
        {"category": "Bridge", "item_num": "B004", "name": "Bridge - Falsework Steel System", "sku": "FALSE-STL", "unit": "SF", "price": 12.50},
        {"category": "Bridge", "item_num": "B005", "name": "Bridge - Falsework Timber System", "sku": "FALSE-TIM", "unit": "SF", "price": 8.75},
        {"category": "Bridge", "item_num": "B006", "name": "Bridge - Barrier Rail Forms", "sku": "BAR-FORM", "unit": "LF", "price": 18.50},
        {"category": "Bridge", "item_num": "B007", "name": "Bridge - Expansion Joints", "sku": "EXP-JNT", "unit": "LF", "price": 125.00},
        {"category": "Bridge", "item_num": "B008", "name": "Bridge - Drainage Scuppers", "sku": "SCUPPER", "unit": "EA", "price": 85.00},
        {"category": "Highway", "item_num": "H004", "name": "Highway - Concrete Barriers", "sku": "CONC-BAR", "unit": "LF", "price": 45.00},
        {"category": "Highway", "item_num": "H005", "name": "Highway - Guard Rail Steel", "sku": "GR-STEEL", "unit": "LF", "price": 28.50},
        {"category": "Highway", "item_num": "H006", "name": "Highway - Retaining Wall Forms", "sku": "RET-FORM", "unit": "SF", "price": 9.50},
        {"category": "Highway", "item_num": "H007", "name": "Highway - Erosion Control Blanket", "sku": "ERO-BLNK", "unit": "SY", "price": 3.25},
    ]
    
    # CATEGORY 7: SITE WORK & UTILITIES  
    sitework_products = [
        {"category": "Excavation", "item_num": "E001", "name": "Excavation - Common Earth", "sku": "EXC-EARTH", "unit": "CY", "price": 8.50},
        {"category": "Excavation", "item_num": "E002", "name": "Excavation - Rock/Solid", "sku": "EXC-ROCK", "unit": "CY", "price": 25.00},
        {"category": "Fill", "item_num": "E003", "name": "Fill - Structural Backfill", "sku": "FILL-STR", "unit": "CY", "price": 15.50},
        {"category": "Fill", "item_num": "E004", "name": "Fill - Select Granular", "sku": "FILL-GRAN", "unit": "CY", "price": 18.75},
        {"category": "Paving", "item_num": "P001", "name": "Paving - Asphalt Concrete 2\"", "sku": "AC-2", "unit": "SY", "price": 12.50},
        {"category": "Paving", "item_num": "P002", "name": "Paving - Asphalt Concrete 3\"", "sku": "AC-3", "unit": "SY", "price": 18.75},
        {"category": "Paving", "item_num": "P003", "name": "Paving - Base Course 6\"", "sku": "BASE-6", "unit": "SY", "price": 8.95},
        {"category": "Drainage", "item_num": "DR001", "name": "Drainage - Storm Pipe 12\" RCP", "sku": "RCP-12", "unit": "LF", "price": 25.50},
        {"category": "Drainage", "item_num": "DR002", "name": "Drainage - Storm Pipe 18\" RCP", "sku": "RCP-18", "unit": "LF", "price": 42.50},
        {"category": "Drainage", "item_num": "DR003", "name": "Drainage - Catch Basin", "sku": "CB-STD", "unit": "EA", "price": 485.00},
        {"category": "Drainage", "item_num": "DR004", "name": "Drainage - Manhole Cover", "sku": "MH-CVR", "unit": "EA", "price": 125.00},
    ]
    
    # CATEGORY 8: ELECTRICAL & SAFETY
    electrical_products = [
        {"category": "Electrical", "item_num": "EL001", "name": "Electrical - Conduit 1\" EMT", "sku": "EMT-1", "unit": "LF", "price": 2.85},
        {"category": "Electrical", "item_num": "EL002", "name": "Electrical - Conduit 2\" PVC", "sku": "PVC-2", "unit": "LF", "price": 3.25},
        {"category": "Electrical", "item_num": "EL003", "name": "Electrical - Junction Box 4x4", "sku": "JB-4X4", "unit": "EA", "price": 8.50},
        {"category": "Electrical", "item_num": "EL004", "name": "Electrical - Wire 12 AWG THHN", "sku": "W-12THHN", "unit": "LF", "price": 0.45},
        {"category": "Safety", "item_num": "SF001", "name": "Safety - Temporary Fence 6'", "sku": "TEMP-FNC", "unit": "LF", "price": 4.25},
        {"category": "Safety", "item_num": "SF002", "name": "Safety - Barricades Type III", "sku": "BAR-T3", "unit": "EA", "price": 125.00},
        {"category": "Safety", "item_num": "SF003", "name": "Safety - Construction Signs", "sku": "SIGN-CON", "unit": "EA", "price": 85.00},
        {"category": "Safety", "item_num": "SF004", "name": "Safety - Traffic Cones 28\"", "sku": "CONE-28", "unit": "EA", "price": 15.50},
    ]
    
    # Combine all products
    all_products = (concrete_products + lumber_products + steel_products + 
                   formwork_products + openings_products + bridge_products + 
                   sitework_products + electrical_products)
    
    catalog_data.extend(all_products)
    
    return catalog_data

def save_catalog_csv(catalog_data, filename="pace_sample_catalog.csv"):
    """Save catalog to CSV file"""
    df = pd.DataFrame(catalog_data)
    df.to_csv(filename, index=False)
    print(f"Catalog saved to {filename}")
    print(f"Total products: {len(catalog_data)}")
    return df

def save_catalog_json(catalog_data, filename="pace_sample_catalog.json"):
    """Save catalog to JSON file"""
    catalog_json = {
        "catalog_info": {
            "name": "PACE Sample Construction Catalog",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "total_products": len(catalog_data)
        },
        "products": catalog_data
    }
    
    with open(filename, 'w') as f:
        json.dump(catalog_json, f, indent=2)
    print(f"Catalog saved to {filename}")
    return catalog_json

def load_into_pace_session():
    """Load catalog data into Streamlit session state for PACE"""
    catalog_data = create_construction_catalog()
    
    # If running in Streamlit context
    try:
        import streamlit as st
        if 'catalog_data' not in st.session_state:
            st.session_state.catalog_data = catalog_data
            st.success(f"Loaded {len(catalog_data)} products into PACE catalog!")
        return catalog_data
    except ImportError:
        # Not in Streamlit context, return data
        return catalog_data

def get_products_by_category(catalog_data, category):
    """Filter products by category"""
    return [product for product in catalog_data if product['category'].lower() == category.lower()]

def search_products(catalog_data, search_term):
    """Search products by name or SKU"""
    search_term = search_term.lower()
    results = []
    for product in catalog_data:
        if (search_term in product['name'].lower() or 
            search_term in product['sku'].lower() or
            search_term in product['category'].lower()):
            results.append(product)
    return results

# Main execution
if __name__ == "__main__":
    print("PACE Construction Catalog Generator")
    print("=" * 50)
    
    # Generate catalog
    catalog = create_construction_catalog()
    
    # Save to files
    df = save_catalog_csv(catalog)
    json_data = save_catalog_json(catalog)
    
    # Display summary
    print(f"\nCatalog Summary:")
    print(f"Total Products: {len(catalog)}")
    
    categories = {}
    for product in catalog:
        cat = product['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print(f"\nProducts by Category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} items")
    
    # Price range
    prices = [p['price'] for p in catalog]
    print(f"\nPrice Range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    print(f"\nFiles created:")
    print(f"  - pace_sample_catalog.csv")
    print(f"  - pace_sample_catalog.json")
    
    print(f"\nTo use in PACE:")
    print(f"  1. Copy this script to your PACE project directory")
    print(f"  2. Run: python catalog_generator.py")
    print(f"  3. Load the CSV file in your PACE catalog section")