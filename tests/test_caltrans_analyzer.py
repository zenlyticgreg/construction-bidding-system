"""
Test script for CalTrans PDF Analyzer

This script demonstrates the functionality of the CalTransPDFAnalyzer
with sample data and provides examples of how to use the analyzer.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzers.caltrans_analyzer import (
    CalTransPDFAnalyzer, 
    analyze_caltrans_pdf,
    extract_quantities_from_text,
    find_caltrans_terms
)


def test_quantity_extraction():
    """Test quantity extraction from sample text"""
    print("=== Testing Quantity Extraction ===")
    
    sample_text = """
    Bridge deck concrete: 2,500 SQFT
    Formwork installation: 1,200 LF
    Baluster installation: 50 EA
    Concrete volume: 500 CY
    Retaining wall: 800 SQFT
    """
    
    quantities = extract_quantities_from_text(sample_text)
    
    print(f"Found {len(quantities)} quantities:")
    for q in quantities:
        print(f"  - {q.value} {q.unit} (context: {q.context[:50]}...)")
    
    return quantities


def test_term_detection():
    """Test CalTrans term detection"""
    print("\n=== Testing Term Detection ===")
    
    sample_text = """
    The project includes BALUSTER installation for bridge railing.
    TYPE_86H_RAIL system will be used for safety barriers.
    Formwork includes BLOCKOUT for utility penetrations.
    STAMPED_CONCRETE finish for architectural treatment.
    RETAINING_WALL construction with FRACTURED_RIB_TEXTURE.
    """
    
    terms = find_caltrans_terms(sample_text)
    
    print(f"Found {len(terms)} CalTrans terms:")
    for term in terms:
        print(f"  - {term.term} ({term.category}, {term.priority} priority)")
        print(f"    Context: {term.context[:80]}...")
    
    return terms


def test_lumber_calculations():
    """Test lumber requirement calculations"""
    print("\n=== Testing Lumber Calculations ===")
    
    analyzer = CalTransPDFAnalyzer()
    
    # Sample quantities
    quantities = [
        analyzer._extract_quantities("Formwork: 5000 SQFT", 1)[0],
        analyzer._extract_quantities("Wall forms: 2000 SQFT", 1)[0],
        analyzer._extract_quantities("Deck forms: 3000 SQFT", 1)[0]
    ]
    
    # Sample terms
    terms = []
    form_terms = analyzer._find_caltrans_terms("FORM_FACING installation", 1, [])
    falsework_terms = analyzer._find_caltrans_terms("FALSEWORK support", 1, [])
    
    if form_terms:
        terms.append(form_terms[0])
    if falsework_terms:
        terms.append(falsework_terms[0])
    
    lumber_req = analyzer.calculate_lumber_requirements(terms, quantities)
    
    print("Lumber Requirements:")
    print(f"  - Total Board Feet: {lumber_req.total_board_feet:.2f}")
    print(f"  - Plywood Sheets: {lumber_req.plywood_sheets:.2f}")
    print(f"  - Formwork Area: {lumber_req.formwork_area:.2f} SQFT")
    print(f"  - Estimated Cost: ${lumber_req.estimated_cost:,.2f}")
    
    return lumber_req


def test_alert_generation():
    """Test alert generation"""
    print("\n=== Testing Alert Generation ===")
    
    analyzer = CalTransPDFAnalyzer()
    
    # Sample data that should generate alerts
    sample_text = """
    BALUSTER installation: 200 EA
    Large concrete pour: 15,000 SQFT
    TYPE_86H_RAIL system: 2000 LF
    """
    
    quantities = analyzer._extract_quantities(sample_text, 1)
    terms = analyzer._find_caltrans_terms(sample_text, 1, quantities)
    alerts = analyzer._generate_alerts(terms, quantities, 1)
    
    print(f"Generated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"  - {alert.level.value.upper()}: {alert.message}")
        if alert.term:
            print(f"    Term: {alert.term}")
        if alert.quantity:
            print(f"    Quantity: {alert.quantity.value} {alert.quantity.unit}")
    
    return alerts


def test_context_extraction():
    """Test context extraction functionality"""
    print("\n=== Testing Context Extraction ===")
    
    analyzer = CalTransPDFAnalyzer()
    
    sample_text = """
    The bridge deck construction includes BALUSTER installation 
    for the railing system. The balusters will be installed at 
    4-foot intervals along the bridge length.
    """
    
    context = analyzer.extract_context(sample_text, "BALUSTER", 30)
    print(f"Extracted context for 'BALUSTER': {context}")
    
    classification = analyzer.classify_quantity_context(
        "Formwork installation for bridge deck concrete"
    )
    print(f"Context classification: {classification}")
    
    return context, classification


def test_analyzer_integration():
    """Test full analyzer integration with sample data"""
    print("\n=== Testing Full Analyzer Integration ===")
    
    # Create a mock PDF analysis result
    analyzer = CalTransPDFAnalyzer()
    
    # Sample comprehensive text
    sample_text = """
    CALTRANS BRIDGE PROJECT SPECIFICATIONS
    
    Bridge Deck Construction:
    - Concrete deck: 25,000 SQFT
    - Formwork installation: 12,000 SQFT
    - BALUSTER installation: 150 EA
    - TYPE_86H_RAIL system: 3,500 LF
    
    Retaining Wall:
    - RETAINING_WALL construction: 8,000 SQFT
    - FRACTURED_RIB_TEXTURE finish
    - Concrete volume: 2,500 CY
    
    Formwork Details:
    - FORM_FACING material: 15,000 SQFT
    - FALSEWORK support: 75 EA
    - BLOCKOUT for utilities: 200 EA
    
    Erosion Control:
    - EROSION_CONTROL measures: 5,000 LF
    """
    
    # Simulate page analysis
    sheet_analysis = analyzer.analyze_page(sample_text, 1)
    
    print("Page Analysis Results:")
    print(f"  - Terms found: {len(sheet_analysis.terms_found)}")
    print(f"  - Quantities found: {len(sheet_analysis.quantities_found)}")
    print(f"  - Alerts generated: {len(sheet_analysis.alerts)}")
    print(f"  - Text quality: {sheet_analysis.text_extraction_quality:.2f}")
    
    # Show high-priority terms
    high_priority = [t for t in sheet_analysis.terms_found if t.priority == "high"]
    print(f"  - High-priority terms: {len(high_priority)}")
    for term in high_priority:
        print(f"    * {term.term}")
    
    return sheet_analysis


def main():
    """Run all tests"""
    print("CalTrans PDF Analyzer Test Suite")
    print("=" * 50)
    
    try:
        # Run individual tests
        test_quantity_extraction()
        test_term_detection()
        test_lumber_calculations()
        test_alert_generation()
        test_context_extraction()
        test_analyzer_integration()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 