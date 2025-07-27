"""
Example usage of CalTrans Bidding Engine

This script demonstrates how to use the CalTransBiddingEngine to generate
complete bid packages from CalTrans PDF files.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bidding.bid_engine import CalTransBiddingEngine, create_bidding_engine


def example_basic_usage():
    """Example of basic bid engine usage"""
    print("=== CalTrans Bidding Engine - Basic Usage Example ===\n")
    
    # Create the bidding engine
    engine = create_bidding_engine()
    print("✓ Bidding engine created successfully")
    
    # Example project information
    project_name = "Bridge Railing Replacement Project"
    project_number = "CA-2024-001"
    markup_percentage = 0.25  # 25% markup
    
    print(f"Project: {project_name}")
    print(f"Project Number: {project_number}")
    print(f"Markup: {markup_percentage * 100}%\n")
    
    # Example PDF path (you would replace this with actual PDF)
    pdf_path = "sample_caltrans_project.pdf"
    
    if os.path.exists(pdf_path):
        try:
            # Generate complete bid
            print("Generating bid package...")
            bid_data = engine.generate_complete_bid(
                pdf_path=pdf_path,
                project_name=project_name,
                project_number=project_number,
                markup_percentage=markup_percentage
            )
            
            # Display results
            print("✓ Bid package generated successfully!\n")
            
            # Show project summary
            print("=== PROJECT SUMMARY ===")
            print(f"Project: {bid_data['project_name']}")
            print(f"Project Number: {bid_data['project_number']}")
            print(f"Bid Date: {bid_data['bid_date']}")
            print(f"Line Items: {bid_data['pricing_summary']['line_item_count']}")
            print(f"High Priority Items: {bid_data['pricing_summary']['high_priority_items']}")
            
            # Show pricing breakdown
            print("\n=== PRICING BREAKDOWN ===")
            pricing = bid_data['pricing_summary']
            print(f"Subtotal: ${pricing['subtotal']:,.2f}")
            print(f"Markup ({markup_percentage * 100}%): ${pricing['markup_amount']:,.2f}")
            print(f"Waste Adjustments: ${pricing['waste_adjustments']:,.2f}")
            print(f"Delivery Fee: ${pricing['delivery_fee']:,.2f}")
            print(f"TOTAL: ${pricing['total']:,.2f}")
            
            # Show line items
            print("\n=== LINE ITEMS ===")
            for item in bid_data['line_items'][:5]:  # Show first 5 items
                print(f"{item['item_number']}: {item['description']}")
                print(f"  Quantity: {item['quantity']} {item['unit']}")
                print(f"  Unit Price: ${item['unit_price']:.2f}")
                print(f"  Total: ${item['total_price']:,.2f}")
                if item['product_matches']:
                    best_match = item['product_matches'][0]
                    print(f"  Best Product: {best_match['product_name']} (${best_match.get('price', best_match.get('estimated_price', 0)):.2f})")
                print()
            
            # Save bid to file
            output_path = f"output/bids/{project_number}_bid.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            engine.save_bid_to_file(bid_data, output_path)
            print(f"✓ Bid saved to: {output_path}")
            
        except Exception as e:
            print(f"✗ Error generating bid: {e}")
    else:
        print(f"✗ PDF file not found: {pdf_path}")
        print("Please provide a valid CalTrans PDF file to test the bid engine.")


def example_product_matching():
    """Example of product matching functionality"""
    print("\n=== Product Matching Example ===\n")
    
    engine = create_bidding_engine()
    
    # Test different CalTrans terms
    test_terms = [
        {"term": "BALUSTER", "category": "bridge_barrier"},
        {"term": "BLOCKOUT", "category": "formwork"},
        {"term": "STAMPED_CONCRETE", "category": "concrete"},
        {"term": "RETAINING_WALL", "category": "formwork"},
        {"term": "EROSION_CONTROL", "category": "temporary_structures"}
    ]
    
    for term_data in test_terms:
        print(f"Finding products for: {term_data['term']} ({term_data['category']})")
        products = engine.find_products_for_term(term_data)
        
        if products:
            print(f"  Found {len(products)} matching products:")
            for i, product in enumerate(products[:2], 1):  # Show top 2
                price = product.get('price') or product.get('estimated_price', 0)
                print(f"    {i}. {product['product_name']} - ${price:.2f} ({product['quality']})")
        else:
            print("  No matching products found")
        print()


def example_quantity_calculation():
    """Example of quantity calculation functionality"""
    print("\n=== Quantity Calculation Example ===\n")
    
    engine = create_bidding_engine()
    
    # Mock quantities (in real usage, these would come from PDF analysis)
    from analyzers.caltrans_analyzer import ExtractedQuantity
    
    mock_quantities = [
        ExtractedQuantity(value=150.0, unit="EA", context="baluster installation", page_number=1),
        ExtractedQuantity(value=200.0, unit="LF", context="railing length", page_number=1),
        ExtractedQuantity(value=500.0, unit="SQFT", context="formwork area", page_number=2),
        ExtractedQuantity(value=25.0, unit="CY", context="concrete volume", page_number=2)
    ]
    
    test_terms = [
        {"term": "BALUSTER", "context": "baluster installation for bridge railing"},
        {"term": "FORMWORK", "context": "formwork for concrete wall"},
        {"term": "CONCRETE", "context": "concrete placement"}
    ]
    
    for term_data in test_terms:
        quantity = engine.calculate_quantity_needed(term_data, mock_quantities)
        print(f"Quantity needed for {term_data['term']}: {quantity:.1f} {engine._determine_unit(term_data['term'])}")


def example_pricing_calculation():
    """Example of pricing calculation functionality"""
    print("\n=== Pricing Calculation Example ===\n")
    
    engine = create_bidding_engine()
    
    # Create sample line items
    from bidding.bid_engine import BidLineItem
    
    sample_line_items = [
        BidLineItem(
            item_number="001",
            description="BALUSTER - bridge_barrier",
            caltrans_term="BALUSTER",
            quantity=150.0,
            unit="EA",
            unit_price=25.0,
            total_price=3750.0,
            waste_factor=0.10,
            markup_percentage=0.20
        ),
        BidLineItem(
            item_number="002",
            description="FORMWORK - concrete",
            caltrans_term="FORMWORK",
            quantity=500.0,
            unit="SQFT",
            unit_price=8.0,
            total_price=4000.0,
            waste_factor=0.10,
            markup_percentage=0.20
        ),
        BidLineItem(
            item_number="003",
            description="HARDWARE - fasteners",
            caltrans_term="HARDWARE",
            quantity=1000.0,
            unit="EA",
            unit_price=2.5,
            total_price=2500.0,
            waste_factor=0.05,
            markup_percentage=0.20
        )
    ]
    
    # Calculate pricing summary
    pricing = engine.calculate_pricing_summary(sample_line_items)
    
    print("=== SAMPLE BID PRICING ===")
    print(f"Subtotal: ${pricing['subtotal']:,.2f}")
    print(f"Markup (20%): ${pricing['markup_amount']:,.2f}")
    print(f"Waste Adjustments: ${pricing['waste_adjustments']:,.2f}")
    print(f"Delivery Fee: ${pricing['delivery_fee']:,.2f}")
    print(f"TOTAL: ${pricing['total']:,.2f}")
    print(f"Line Items: {pricing['line_item_count']}")
    print(f"High Priority Items: {pricing['high_priority_items']}")
    print(f"Estimated Materials Cost: ${pricing['estimated_materials_cost']:,.2f}")
    print(f"Estimated Labor Cost: ${pricing['estimated_labor_cost']:,.2f}")


def main():
    """Main example function"""
    print("CalTrans Bidding Engine - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_product_matching()
    example_quantity_calculation()
    example_pricing_calculation()
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("\nTo use with real data:")
    print("1. Place your CalTrans PDF in the project directory")
    print("2. Update the pdf_path variable in the script")
    print("3. Run the script to generate a complete bid package")


if __name__ == "__main__":
    main() 