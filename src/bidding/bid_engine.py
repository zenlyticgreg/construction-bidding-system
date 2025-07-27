"""
CalTrans Bidding Engine

This module provides a comprehensive bidding engine that combines CalTrans PDF analysis
with Whitecap product matching to generate complete bid packages with line items,
pricing calculations, and project-specific configurations.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json

# Local imports
try:
    from analyzers.caltrans_analyzer import CalTransPDFAnalyzer, CalTransAnalysisResult, TermMatch, ExtractedQuantity
    from analyzers.product_matcher import ProductMatcher, ProductMatch
except ImportError:
    # Fallback for testing without full project structure
    CalTransPDFAnalyzer = None
    CalTransAnalysisResult = None
    TermMatch = None
    ExtractedQuantity = None
    ProductMatcher = None
    ProductMatch = None


class WasteFactor(Enum):
    """Waste factors for different material categories"""
    FORMWORK = 0.10  # 10%
    LUMBER = 0.10    # 10%
    HARDWARE = 0.05  # 5%
    SPECIALTY = 0.15 # 15%
    DEFAULT = 0.08   # 8%


class PricingConfig:
    """Configuration for pricing calculations"""
    DEFAULT_MARKUP = 0.20  # 20%
    DELIVERY_PERCENTAGE = 0.03  # 3%
    DELIVERY_MINIMUM = 150.00  # $150 minimum
    WASTE_FACTORS = {
        "formwork": WasteFactor.FORMWORK.value,
        "lumber": WasteFactor.LUMBER.value,
        "hardware": WasteFactor.HARDWARE.value,
        "specialty": WasteFactor.SPECIALTY.value,
        "default": WasteFactor.DEFAULT.value
    }


@dataclass
class BidLineItem:
    """Represents a single line item in a bid"""
    item_number: str
    description: str
    caltrans_term: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    product_matches: List[Dict[str, Any]] = field(default_factory=list)
    waste_factor: float = 0.08
    markup_percentage: float = 0.20
    delivery_fee: float = 0.0
    notes: str = ""
    confidence: float = 1.0


@dataclass
class PricingSummary:
    """Summary of bid pricing calculations"""
    subtotal: float = 0.0
    markup_amount: float = 0.0
    delivery_fee: float = 0.0
    waste_adjustments: float = 0.0
    total: float = 0.0
    line_item_count: int = 0
    high_priority_items: int = 0
    estimated_materials_cost: float = 0.0
    estimated_labor_cost: float = 0.0


@dataclass
class BidPackage:
    """Complete bid package with all components"""
    project_name: str
    project_number: str
    bid_date: datetime = field(default_factory=datetime.now)
    line_items: List[BidLineItem] = field(default_factory=list)
    pricing_summary: PricingSummary = field(default_factory=PricingSummary)
    analysis_results: Optional[CalTransAnalysisResult] = None
    markup_percentage: float = 0.20
    delivery_fee: float = 0.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CalTransBiddingEngine:
    """
    Comprehensive bidding engine for CalTrans projects.
    
    Features:
    - Combines CalTrans analysis with Whitecap product matching
    - Generates complete bid packages with line items
    - Applies markup, delivery fees, and waste factors
    - Calculates quantities based on CalTrans terminology
    - Provides bid summary with pricing breakdown
    - Handles project-specific configurations
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the bidding engine"""
        self.logger = logger or self._setup_logger()
        
        # Initialize analyzers
        self.caltrans_analyzer = CalTransPDFAnalyzer(logger) if CalTransPDFAnalyzer else None
        self.product_matcher = ProductMatcher(logger) if ProductMatcher else None
        
        # Product matching strategies for different CalTrans terms
        self.matching_strategies = {
            "BALUSTER": ["concrete", "form", "heavy", "plywood", "CDX"],
            "BLOCKOUT": ["lumber", "2x4", "2x6", "construction", "grade"],
            "STAMPED_CONCRETE": ["texture", "form", "liner", "pattern"],
            "RETAINING_WALL": ["form", "tie", "plywood", "wall"],
            "EROSION_CONTROL": ["post", "stake", "treated", "fence"],
            "FORMWORK": ["plywood", "form", "CDX", "sheathing"],
            "FALSEWORK": ["lumber", "support", "temporary", "structure"],
            "BRIDGE_RAILING": ["steel", "rail", "post", "hardware"],
            "CONCRETE_FINISHING": ["tool", "finish", "texture", "pattern"],
            "TEMPORARY_STRUCTURES": ["lumber", "plywood", "hardware", "support"]
        }
        
        # Quantity calculation factors
        self.quantity_factors = {
            "BALUSTER": {"base_factor": 1.0, "unit": "EA"},
            "BLOCKOUT": {"base_factor": 1.0, "unit": "EA"},
            "STAMPED_CONCRETE": {"base_factor": 1.0, "unit": "SQFT"},
            "RETAINING_WALL": {"base_factor": 1.0, "unit": "SQFT"},
            "EROSION_CONTROL": {"base_factor": 1.0, "unit": "LF"},
            "FORMWORK": {"base_factor": 1.0, "unit": "SQFT"},
            "FALSEWORK": {"base_factor": 1.0, "unit": "SQFT"},
            "BRIDGE_RAILING": {"base_factor": 1.0, "unit": "LF"},
            "CONCRETE_FINISHING": {"base_factor": 1.0, "unit": "SQFT"},
            "TEMPORARY_STRUCTURES": {"base_factor": 1.0, "unit": "EA"}
        }
        
        self.logger.info("CalTransBiddingEngine initialized successfully")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the bidding engine"""
        logger = logging.getLogger("caltrans_bidding_engine")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def generate_complete_bid(
        self, 
        pdf_path: str, 
        project_name: str, 
        project_number: str, 
        markup_percentage: float = 0.20
    ) -> Dict[str, Any]:
        """
        Generate a complete bid package from a CalTrans PDF.
        
        Args:
            pdf_path: Path to the CalTrans PDF file
            project_name: Name of the project
            project_number: Project number
            markup_percentage: Markup percentage (default 20%)
            
        Returns:
            Dictionary containing the complete bid package
        """
        self.logger.info(f"Generating bid for project: {project_name} ({project_number})")
        
        try:
            # Step 1: Analyze the CalTrans PDF
            if not self.caltrans_analyzer:
                raise RuntimeError("CalTrans analyzer not available")
            
            analysis_result = self.caltrans_analyzer.analyze_pdf(pdf_path)
            self.logger.info(f"PDF analysis completed: {len(analysis_result.terminology_found)} terms found")
            
            # Step 2: Create bid package
            bid_package = BidPackage(
                project_name=project_name,
                project_number=project_number,
                markup_percentage=markup_percentage,
                analysis_results=analysis_result
            )
            
            # Step 3: Generate line items from analysis results
            line_items = self._generate_line_items_from_analysis(analysis_result)
            bid_package.line_items = line_items
            
            # Step 4: Calculate pricing summary
            pricing_summary = self.calculate_pricing_summary(line_items, markup_percentage)
            bid_package.pricing_summary = pricing_summary
            
            # Step 5: Calculate delivery fee
            delivery_fee = self._calculate_delivery_fee(pricing_summary.subtotal)
            bid_package.delivery_fee = delivery_fee
            pricing_summary.delivery_fee = delivery_fee
            pricing_summary.total += delivery_fee
            
            # Step 6: Convert to dictionary format
            result = self._bid_package_to_dict(bid_package)
            
            self.logger.info(f"Bid generation completed: {len(line_items)} line items, total: ${pricing_summary.total:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating bid: {e}")
            raise
    
    def find_products_for_term(self, term_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find matching products for a CalTrans term.
        
        Args:
            term_data: Dictionary containing term information
            
        Returns:
            List of matching products with scores and pricing
        """
        if not self.product_matcher:
            return []
        
        term = term_data.get("term", "")
        category = term_data.get("category", "")
        
        # Get matching strategy for this term
        search_terms = self.matching_strategies.get(term.upper(), [term.lower()])
        
        # Add category-specific terms
        if category:
            search_terms.extend([category.lower()])
        
        # Find products
        products = self.product_matcher.find_products_by_terms(search_terms)
        
        # Limit to top 3 matches
        return products[:3]
    
    def calculate_quantity_needed(self, term_data: Dict[str, Any], all_quantities: List[ExtractedQuantity]) -> float:
        """
        Calculate the quantity needed for a specific term.
        
        Args:
            term_data: Dictionary containing term information
            all_quantities: List of all extracted quantities
            
        Returns:
            Calculated quantity needed
        """
        term = term_data.get("term", "")
        context = term_data.get("context", "")
        
        # Find associated quantities
        associated_quantities = []
        for quantity in all_quantities:
            # Check if quantity is associated with this term
            if (term.lower() in quantity.context.lower() or 
                quantity.context.lower() in context.lower()):
                associated_quantities.append(quantity)
        
        if not associated_quantities:
            # If no direct association, use the first quantity with matching unit
            term_factors = self.quantity_factors.get(term.upper(), {})
            target_unit = term_factors.get("unit", "EA")
            
            for quantity in all_quantities:
                if quantity.unit == target_unit:
                    associated_quantities.append(quantity)
                    break
        
        # Calculate total quantity
        total_quantity = sum(q.value for q in associated_quantities)
        
        # Apply base factor if available
        term_factors = self.quantity_factors.get(term.upper(), {})
        base_factor = term_factors.get("base_factor", 1.0)
        
        return total_quantity * base_factor
    
    def calculate_pricing_summary(self, bid_line_items: List[BidLineItem]) -> Dict[str, Any]:
        """
        Calculate pricing summary for bid line items.
        
        Args:
            bid_line_items: List of bid line items
            
        Returns:
            Dictionary containing pricing summary
        """
        subtotal = sum(item.total_price for item in bid_line_items)
        
        # Calculate markup (using average markup from line items)
        if bid_line_items:
            avg_markup = sum(item.markup_percentage for item in bid_line_items) / len(bid_line_items)
            markup_amount = subtotal * avg_markup
        else:
            markup_amount = 0.0
        
        # Calculate waste adjustments
        waste_adjustments = sum(
            item.total_price * item.waste_factor for item in bid_line_items
        )
        
        # Calculate delivery fee
        delivery_fee = self._calculate_delivery_fee(subtotal)
        
        # Calculate total
        total = subtotal + markup_amount + waste_adjustments + delivery_fee
        
        # Count high priority items
        high_priority_items = len([
            item for item in bid_line_items 
            if any("high" in match.get("quality", "").lower() 
                   for match in item.product_matches)
        ])
        
        # Estimate materials and labor costs
        estimated_materials_cost = subtotal * 0.7  # 70% materials
        estimated_labor_cost = subtotal * 0.3      # 30% labor
        
        summary = PricingSummary(
            subtotal=subtotal,
            markup_amount=markup_amount,
            delivery_fee=delivery_fee,
            waste_adjustments=waste_adjustments,
            total=total,
            line_item_count=len(bid_line_items),
            high_priority_items=high_priority_items,
            estimated_materials_cost=estimated_materials_cost,
            estimated_labor_cost=estimated_labor_cost
        )
        
        return {
            "subtotal": summary.subtotal,
            "markup_amount": summary.markup_amount,
            "delivery_fee": summary.delivery_fee,
            "waste_adjustments": summary.waste_adjustments,
            "total": summary.total,
            "line_item_count": summary.line_item_count,
            "high_priority_items": summary.high_priority_items,
            "estimated_materials_cost": summary.estimated_materials_cost,
            "estimated_labor_cost": summary.estimated_labor_cost
        }
    
    def _generate_line_items_from_analysis(self, analysis_result: CalTransAnalysisResult) -> List[BidLineItem]:
        """Generate line items from CalTrans analysis results"""
        line_items = []
        item_number = 1
        
        # Group terms by category for better organization
        terms_by_category = {}
        for term in analysis_result.terminology_found:
            category = term.category
            if category not in terms_by_category:
                terms_by_category[category] = []
            terms_by_category[category].append(term)
        
        # Generate line items for each category
        for category, terms in terms_by_category.items():
            for term in terms:
                try:
                    # Calculate quantity needed
                    quantity = self.calculate_quantity_needed(
                        {"term": term.term, "context": term.context},
                        analysis_result.quantities
                    )
                    
                    if quantity <= 0:
                        continue
                    
                    # Find matching products
                    products = self.find_products_for_term({
                        "term": term.term,
                        "category": term.category
                    })
                    
                    # Calculate unit price from best product match
                    unit_price = self._calculate_unit_price_from_products(products)
                    
                    # Determine waste factor
                    waste_factor = self._determine_waste_factor(term.term, term.category)
                    
                    # Calculate total price
                    total_price = quantity * unit_price * (1 + waste_factor)
                    
                    # Create line item
                    line_item = BidLineItem(
                        item_number=f"{item_number:03d}",
                        description=f"{term.term} - {term.category}",
                        caltrans_term=term.term,
                        quantity=quantity,
                        unit=self._determine_unit(term.term),
                        unit_price=unit_price,
                        total_price=total_price,
                        product_matches=products,
                        waste_factor=waste_factor,
                        notes=f"Page {term.page_number}: {term.context[:100]}..."
                    )
                    
                    line_items.append(line_item)
                    item_number += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error generating line item for term {term.term}: {e}")
                    continue
        
        return line_items
    
    def _calculate_unit_price_from_products(self, products: List[Dict[str, Any]]) -> float:
        """Calculate unit price from product matches"""
        if not products:
            return 0.0
        
        # Use the best match (first product)
        best_product = products[0]
        
        # Use actual price if available, otherwise estimated price
        price = best_product.get("price") or best_product.get("estimated_price", 0.0)
        
        return price
    
    def _determine_waste_factor(self, term: str, category: str) -> float:
        """Determine waste factor for a term/category"""
        term_upper = term.upper()
        
        # Check for specific term-based waste factors
        if "FORM" in term_upper or "PLYWOOD" in term_upper:
            return PricingConfig.WASTE_FACTORS["formwork"]
        elif "LUMBER" in term_upper or "2X" in term_upper or "4X" in term_upper:
            return PricingConfig.WASTE_FACTORS["lumber"]
        elif "BOLT" in term_upper or "SCREW" in term_upper or "NAIL" in term_upper:
            return PricingConfig.WASTE_FACTORS["hardware"]
        elif "SPECIAL" in term_upper or "CUSTOM" in term_upper:
            return PricingConfig.WASTE_FACTORS["specialty"]
        
        # Check category-based waste factors
        category_lower = category.lower()
        if "formwork" in category_lower:
            return PricingConfig.WASTE_FACTORS["formwork"]
        elif "lumber" in category_lower:
            return PricingConfig.WASTE_FACTORS["lumber"]
        elif "hardware" in category_lower:
            return PricingConfig.WASTE_FACTORS["hardware"]
        
        return PricingConfig.WASTE_FACTORS["default"]
    
    def _determine_unit(self, term: str) -> str:
        """Determine the appropriate unit for a term"""
        term_upper = term.upper()
        
        # Check quantity factors for specific terms
        if term_upper in self.quantity_factors:
            return self.quantity_factors[term_upper]["unit"]
        
        # Default unit determination based on term content
        if any(word in term_upper for word in ["BALUSTER", "BLOCKOUT", "POST", "PIECE"]):
            return "EA"
        elif any(word in term_upper for word in ["WALL", "FORM", "FINISH", "TEXTURE"]):
            return "SQFT"
        elif any(word in term_upper for word in ["RAIL", "FENCE", "CONTROL"]):
            return "LF"
        elif any(word in term_upper for word in ["CONCRETE", "MATERIAL"]):
            return "CY"
        
        return "EA"  # Default to each
    
    def _calculate_delivery_fee(self, subtotal: float) -> float:
        """Calculate delivery fee based on subtotal"""
        delivery_fee = subtotal * PricingConfig.DELIVERY_PERCENTAGE
        return max(delivery_fee, PricingConfig.DELIVERY_MINIMUM)
    
    def _bid_package_to_dict(self, bid_package: BidPackage) -> Dict[str, Any]:
        """Convert bid package to dictionary format"""
        return {
            "project_name": bid_package.project_name,
            "project_number": bid_package.project_number,
            "bid_date": bid_package.bid_date.isoformat(),
            "markup_percentage": bid_package.markup_percentage,
            "delivery_fee": bid_package.delivery_fee,
            "notes": bid_package.notes,
            "line_items": [
                {
                    "item_number": item.item_number,
                    "description": item.description,
                    "caltrans_term": item.caltrans_term,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "waste_factor": item.waste_factor,
                    "markup_percentage": item.markup_percentage,
                    "delivery_fee": item.delivery_fee,
                    "notes": item.notes,
                    "confidence": item.confidence,
                    "product_matches": item.product_matches
                }
                for item in bid_package.line_items
            ],
            "pricing_summary": {
                "subtotal": bid_package.pricing_summary.subtotal,
                "markup_amount": bid_package.pricing_summary.markup_amount,
                "delivery_fee": bid_package.pricing_summary.delivery_fee,
                "waste_adjustments": bid_package.pricing_summary.waste_adjustments,
                "total": bid_package.pricing_summary.total,
                "line_item_count": bid_package.pricing_summary.line_item_count,
                "high_priority_items": bid_package.pricing_summary.high_priority_items,
                "estimated_materials_cost": bid_package.pricing_summary.estimated_materials_cost,
                "estimated_labor_cost": bid_package.pricing_summary.estimated_labor_cost
            },
            "analysis_metadata": {
                "total_terms_found": len(bid_package.analysis_results.terminology_found) if bid_package.analysis_results else 0,
                "total_quantities": len(bid_package.analysis_results.quantities) if bid_package.analysis_results else 0,
                "high_priority_terms": bid_package.analysis_results.high_priority_terms if bid_package.analysis_results else 0,
                "critical_alerts": bid_package.analysis_results.critical_alerts if bid_package.analysis_results else 0
            } if bid_package.analysis_results else {},
            "metadata": bid_package.metadata
        }
    
    def save_bid_to_file(self, bid_data: Dict[str, Any], output_path: str) -> None:
        """Save bid data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(bid_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Bid saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving bid to file: {e}")
            raise
    
    def load_bid_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load bid data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bid_data = json.load(f)
            self.logger.info(f"Bid loaded from: {file_path}")
            return bid_data
        except Exception as e:
            self.logger.error(f"Error loading bid from file: {e}")
            raise


def create_bidding_engine() -> CalTransBiddingEngine:
    """Factory function to create a CalTransBiddingEngine instance"""
    return CalTransBiddingEngine()


# Example usage and testing functions
def test_bidding_engine():
    """Test the CalTransBiddingEngine functionality"""
    engine = CalTransBiddingEngine()
    
    # Test product matching
    term_data = {"term": "BALUSTER", "category": "bridge_barrier"}
    products = engine.find_products_for_term(term_data)
    print(f"Found {len(products)} products for BALUSTER")
    
    # Test quantity calculation
    quantities = [
        ExtractedQuantity(value=100.0, unit="EA", context="baluster installation", page_number=1),
        ExtractedQuantity(value=50.0, unit="LF", context="railing length", page_number=1)
    ]
    quantity_needed = engine.calculate_quantity_needed(term_data, quantities)
    print(f"Quantity needed for BALUSTER: {quantity_needed}")
    
    # Test pricing summary
    line_items = [
        BidLineItem(
            item_number="001",
            description="Test Item",
            caltrans_term="BALUSTER",
            quantity=100.0,
            unit="EA",
            unit_price=25.0,
            total_price=2500.0
        )
    ]
    pricing = engine.calculate_pricing_summary(line_items)
    print(f"Pricing summary: {pricing}")
    
    return engine


if __name__ == "__main__":
    test_bidding_engine() 