"""
Pricing Calculator for CalTrans Bidding System

This module provides comprehensive pricing calculations including:
- Base pricing calculations with product matching
- Volume discounts and rush order fees
- Regional pricing adjustments
- Delivery optimization and cost calculation
- Pricing history tracking and trend analysis
- Lumber quantity estimation from CalTrans analysis
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import math
import statistics

# Local imports
try:
    from analyzers.caltrans_analyzer import CalTransAnalysisResult, TermMatch, ExtractedQuantity
    from utils.data_validator import ValidationResult, ValidationLevel
except ImportError:
    # Fallback for testing without full project structure
    CalTransAnalysisResult = None
    TermMatch = None
    ExtractedQuantity = None
    
    class ValidationResult:
        """Fallback validation result for testing"""
        def __init__(self, is_valid: bool, level: str, message: str):
            self.is_valid = is_valid
            self.level = level
            self.message = message
    
    class ValidationLevel:
        """Fallback validation level for testing"""
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"


class PricingTier(Enum):
    """Pricing tiers for volume discounts"""
    TIER_1 = (0, 10000)      # 0-10k: No discount
    TIER_2 = (10000, 50000)  # 10k-50k: 5% discount
    TIER_3 = (50000, 100000) # 50k-100k: 10% discount
    TIER_4 = (100000, 250000) # 100k-250k: 15% discount
    TIER_5 = (250000, float('inf')) # 250k+: 20% discount


class RushOrderLevel(Enum):
    """Rush order fee levels"""
    STANDARD = 0.0    # No rush fee
    EXPEDITED = 0.05  # 5% rush fee
    URGENT = 0.10     # 10% rush fee
    CRITICAL = 0.20   # 20% rush fee


class DeliveryZone(Enum):
    """Delivery zones with associated fees"""
    LOCAL = (0.02, 100)      # 2%, $100 minimum
    REGIONAL = (0.04, 200)   # 4%, $200 minimum
    STATEWIDE = (0.06, 350)  # 6%, $350 minimum
    INTERSTATE = (0.08, 500) # 8%, $500 minimum
    REMOTE = (0.12, 750)     # 12%, $750 minimum


@dataclass
class LineItem:
    """Represents a line item for pricing calculations"""
    item_id: str
    description: str
    quantity: float
    unit: str
    base_unit_price: float
    category: str
    supplier: str
    lead_time_days: int = 14
    min_order_quantity: float = 0.0
    bulk_pricing_available: bool = False
    regional_adjustment_factor: float = 1.0
    notes: str = ""


@dataclass
class PricingHistory:
    """Historical pricing data for trend analysis"""
    item_id: str
    date: datetime
    unit_price: float
    quantity: float
    supplier: str
    region: str
    market_conditions: str
    notes: str = ""


@dataclass
class VolumeDiscount:
    """Volume discount configuration"""
    tier: PricingTier
    discount_percentage: float
    minimum_amount: float
    maximum_amount: float


@dataclass
class RegionalPricing:
    """Regional pricing adjustment"""
    region: str
    adjustment_factor: float
    delivery_zone: DeliveryZone
    fuel_surcharge: float = 0.0
    local_tax_rate: float = 0.0


@dataclass
class PricingResult:
    """Result of pricing calculations"""
    line_items: List[LineItem]
    subtotal: float
    volume_discount_amount: float
    volume_discount_percentage: float
    rush_order_fee: float
    rush_order_level: RushOrderLevel
    delivery_fee: float
    delivery_zone: DeliveryZone
    regional_adjustments: float
    tax_amount: float
    total: float
    pricing_confidence: float
    estimated_delivery_days: int
    notes: List[str] = field(default_factory=list)


class PricingCalculator:
    """
    Comprehensive pricing calculator for CalTrans bidding system.
    
    Features:
    - Complex pricing calculations with product matching
    - Volume discounts and rush order fees
    - Regional pricing adjustments
    - Delivery optimization
    - Pricing history tracking and trend analysis
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the pricing calculator"""
        self.logger = logger or self._setup_logger()
        
        # Load configuration
        self.volume_discounts = self._load_volume_discounts()
        self.regional_pricing = self._load_regional_pricing()
        self.pricing_history = self._load_pricing_history()
        
        # Default settings
        self.default_markup_percentage = 0.20  # 20%
        self.default_rush_order_level = RushOrderLevel.STANDARD
        self.default_delivery_zone = DeliveryZone.REGIONAL
        self.pricing_confidence_threshold = 0.8
        
        self.logger.info("PricingCalculator initialized successfully")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the pricing calculator"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_volume_discounts(self) -> List[VolumeDiscount]:
        """Load volume discount configurations"""
        return [
            VolumeDiscount(PricingTier.TIER_1, 0.00, 0, 10000),
            VolumeDiscount(PricingTier.TIER_2, 0.05, 10000, 50000),
            VolumeDiscount(PricingTier.TIER_3, 0.10, 50000, 100000),
            VolumeDiscount(PricingTier.TIER_4, 0.15, 100000, 250000),
            VolumeDiscount(PricingTier.TIER_5, 0.20, 250000, float('inf'))
        ]
    
    def _load_regional_pricing(self) -> Dict[str, RegionalPricing]:
        """Load regional pricing configurations"""
        return {
            "northern_california": RegionalPricing(
                "northern_california", 1.05, DeliveryZone.REGIONAL, 0.02, 0.085
            ),
            "central_california": RegionalPricing(
                "central_california", 1.02, DeliveryZone.LOCAL, 0.01, 0.075
            ),
            "southern_california": RegionalPricing(
                "southern_california", 1.08, DeliveryZone.STATEWIDE, 0.03, 0.095
            ),
            "eastern_california": RegionalPricing(
                "eastern_california", 1.12, DeliveryZone.REMOTE, 0.04, 0.065
            ),
            "coastal_california": RegionalPricing(
                "coastal_california", 1.06, DeliveryZone.REGIONAL, 0.025, 0.085
            )
        }
    
    def _load_pricing_history(self) -> List[PricingHistory]:
        """Load historical pricing data"""
        # This would typically load from a database or file
        # For now, return empty list
        return []
    
    def calculate_base_pricing(self, line_items: List[LineItem]) -> Dict[str, Any]:
        """
        Calculate base pricing for line items.
        
        Args:
            line_items: List of line items to price
            
        Returns:
            Dictionary containing base pricing calculations
        """
        self.logger.info(f"Calculating base pricing for {len(line_items)} line items")
        
        results = {
            "line_items": [],
            "subtotal": 0.0,
            "item_count": len(line_items),
            "categories": {},
            "suppliers": {},
            "pricing_confidence": 1.0
        }
        
        total_confidence = 0.0
        
        for item in line_items:
            # Calculate item total
            item_total = item.quantity * item.base_unit_price
            
            # Apply regional adjustment
            regional_price = item_total * item.regional_adjustment_factor
            
            # Check for bulk pricing
            if item.bulk_pricing_available and item.quantity >= item.min_order_quantity:
                bulk_discount = self._calculate_bulk_discount(item)
                regional_price *= (1 - bulk_discount)
            
            # Calculate pricing confidence based on historical data
            confidence = self._calculate_pricing_confidence(item)
            total_confidence += confidence
            
            item_result = {
                "item_id": item.item_id,
                "description": item.description,
                "quantity": item.quantity,
                "unit": item.unit,
                "base_unit_price": item.base_unit_price,
                "regional_unit_price": item.base_unit_price * item.regional_adjustment_factor,
                "item_total": regional_price,
                "category": item.category,
                "supplier": item.supplier,
                "confidence": confidence,
                "bulk_discount_applied": item.bulk_pricing_available and item.quantity >= item.min_order_quantity
            }
            
            results["line_items"].append(item_result)
            results["subtotal"] += regional_price
            
            # Track categories and suppliers
            if item.category not in results["categories"]:
                results["categories"][item.category] = {"count": 0, "total": 0.0}
            results["categories"][item.category]["count"] += 1
            results["categories"][item.category]["total"] += regional_price
            
            if item.supplier not in results["suppliers"]:
                results["suppliers"][item.supplier] = {"count": 0, "total": 0.0}
            results["suppliers"][item.supplier]["count"] += 1
            results["suppliers"][item.supplier]["total"] += regional_price
        
        # Calculate average confidence
        if line_items:
            results["pricing_confidence"] = total_confidence / len(line_items)
        
        self.logger.info(f"Base pricing calculated: ${results['subtotal']:.2f}")
        return results
    
    def apply_markups(self, subtotal: float, markup_percentage: float) -> float:
        """
        Apply markup to subtotal.
        
        Args:
            subtotal: Base subtotal amount
            markup_percentage: Markup percentage as decimal (e.g., 0.20 for 20%)
            
        Returns:
            Markup amount
        """
        if markup_percentage < 0:
            self.logger.warning(f"Negative markup percentage provided: {markup_percentage}")
            markup_percentage = 0
        
        markup_amount = subtotal * markup_percentage
        self.logger.info(f"Applied {markup_percentage*100:.1f}% markup: ${markup_amount:.2f}")
        return markup_amount
    
    def calculate_delivery_fees(self, subtotal: float, delivery_zone: DeliveryZone) -> float:
        """
        Calculate delivery fees based on subtotal and delivery zone.
        
        Args:
            subtotal: Order subtotal
            delivery_zone: Delivery zone enum
            
        Returns:
            Delivery fee amount
        """
        percentage, minimum = delivery_zone.value
        
        # Calculate base delivery fee
        delivery_fee = subtotal * percentage
        
        # Apply minimum fee if necessary
        delivery_fee = max(delivery_fee, minimum)
        
        # Apply fuel surcharge based on current market conditions
        fuel_surcharge = self._calculate_fuel_surcharge(delivery_zone)
        delivery_fee += fuel_surcharge
        
        self.logger.info(f"Delivery fee calculated: ${delivery_fee:.2f} for zone {delivery_zone.name}")
        return delivery_fee
    
    def apply_volume_discounts(self, subtotal: float, threshold: float = 0.0) -> float:
        """
        Apply volume discounts based on order total.
        
        Args:
            subtotal: Order subtotal
            threshold: Minimum threshold for volume discounts
            
        Returns:
            Volume discount amount
        """
        if subtotal < threshold:
            return 0.0
        
        # Find applicable discount tier
        applicable_discount = None
        for discount in self.volume_discounts:
            if discount.minimum_amount <= subtotal < discount.maximum_amount:
                applicable_discount = discount
                break
        
        if applicable_discount:
            discount_amount = subtotal * applicable_discount.discount_percentage
            self.logger.info(
                f"Applied volume discount: {applicable_discount.discount_percentage*100:.1f}% "
                f"(${discount_amount:.2f}) for tier {applicable_discount.tier.name}"
            )
            return discount_amount
        
        return 0.0
    
    def estimate_lumber_quantities(self, caltrans_analysis: CalTransAnalysisResult) -> Dict[str, Any]:
        """
        Estimate lumber quantities from CalTrans analysis.
        
        Args:
            caltrans_analysis: CalTrans analysis results
            
        Returns:
            Dictionary containing lumber quantity estimates
        """
        if not caltrans_analysis:
            self.logger.warning("No CalTrans analysis provided for lumber estimation")
            return {}
        
        self.logger.info("Estimating lumber quantities from CalTrans analysis")
        
        # Extract formwork and lumber-related terms
        formwork_terms = [
            term for term in caltrans_analysis.terminology_found
            if "formwork" in term.term.lower() or "forming" in term.term.lower()
        ]
        
        lumber_terms = [
            term for term in caltrans_analysis.terminology_found
            if any(keyword in term.term.lower() for keyword in [
                "lumber", "wood", "timber", "board", "plywood", "osb"
            ])
        ]
        
        # Calculate formwork area
        formwork_area = 0.0
        for term in formwork_terms:
            associated_quantities = [
                q for q in caltrans_analysis.quantities
                if self._is_quantity_related_to_term(q, term)
            ]
            for qty in associated_quantities:
                if qty.unit.upper() in ["SQFT", "SF", "SQ.FT"]:
                    formwork_area += qty.value
                elif qty.unit.upper() in ["LF", "LINEAR.FT"]:
                    # Assume 8-foot height for linear measurements
                    formwork_area += qty.value * 8
        
        # Calculate lumber requirements
        lumber_requirements = {
            "formwork_area_sqft": formwork_area,
            "plywood_sheets": math.ceil(formwork_area / 32),  # 4x8 sheets = 32 sqft
            "dimensional_lumber": {
                "2x4": math.ceil(formwork_area * 0.5),  # 2x4s every 2 feet
                "2x6": math.ceil(formwork_area * 0.3),  # 2x6s for headers
                "4x4": math.ceil(formwork_area * 0.1),  # 4x4 posts
            },
            "fasteners": {
                "nails_lbs": formwork_area * 0.5,  # 0.5 lbs per sqft
                "screws_lbs": formwork_area * 0.3,  # 0.3 lbs per sqft
            },
            "waste_factor": 0.15,  # 15% waste factor
            "reuse_factor": 3.0,   # Can reuse formwork 3 times
        }
        
        # Apply waste factor
        for category in ["plywood_sheets", "dimensional_lumber", "fasteners"]:
            if category == "dimensional_lumber":
                for size in lumber_requirements[category]:
                    lumber_requirements[category][size] = math.ceil(
                        lumber_requirements[category][size] * (1 + lumber_requirements["waste_factor"])
                    )
            elif category == "fasteners":
                for fastener_type in lumber_requirements[category]:
                    lumber_requirements[category][fastener_type] = math.ceil(
                        lumber_requirements[category][fastener_type] * (1 + lumber_requirements["waste_factor"])
                    )
            else:
                lumber_requirements[category] = math.ceil(
                    lumber_requirements[category] * (1 + lumber_requirements["waste_factor"])
                )
        
        # Calculate estimated costs
        estimated_costs = {
            "plywood_cost": lumber_requirements["plywood_sheets"] * 45.0,  # $45 per sheet
            "dimensional_lumber_cost": sum(
                count * self._get_lumber_price(size)
                for size, count in lumber_requirements["dimensional_lumber"].items()
            ),
            "fasteners_cost": (
                lumber_requirements["fasteners"]["nails_lbs"] * 2.5 +  # $2.50/lb
                lumber_requirements["fasteners"]["screws_lbs"] * 8.0   # $8.00/lb
            ),
            "total_materials_cost": 0.0
        }
        
        estimated_costs["total_materials_cost"] = (
            estimated_costs["plywood_cost"] +
            estimated_costs["dimensional_lumber_cost"] +
            estimated_costs["fasteners_cost"]
        )
        
        results = {
            "lumber_requirements": lumber_requirements,
            "estimated_costs": estimated_costs,
            "analysis_summary": {
                "formwork_terms_found": len(formwork_terms),
                "lumber_terms_found": len(lumber_terms),
                "total_quantities_analyzed": len(caltrans_analysis.quantities),
                "confidence_score": self._calculate_lumber_estimation_confidence(caltrans_analysis)
            }
        }
        
        self.logger.info(f"Lumber estimation complete: ${estimated_costs['total_materials_cost']:.2f}")
        return results
    
    def calculate_complete_pricing(
        self,
        line_items: List[LineItem],
        region: str = "central_california",
        rush_order_level: RushOrderLevel = RushOrderLevel.STANDARD,
        markup_percentage: float = 0.20
    ) -> PricingResult:
        """
        Calculate complete pricing including all fees and adjustments.
        
        Args:
            line_items: List of line items
            region: Regional pricing zone
            rush_order_level: Rush order fee level
            markup_percentage: Markup percentage
            
        Returns:
            Complete pricing result
        """
        self.logger.info("Calculating complete pricing package")
        
        # Calculate base pricing
        base_pricing = self.calculate_base_pricing(line_items)
        subtotal = base_pricing["subtotal"]
        
        # Apply volume discounts
        volume_discount_amount = self.apply_volume_discounts(subtotal)
        volume_discount_percentage = (volume_discount_amount / subtotal) if subtotal > 0 else 0.0
        
        # Apply markup
        markup_amount = self.apply_markups(subtotal - volume_discount_amount, markup_percentage)
        
        # Calculate rush order fee
        rush_order_fee = self._calculate_rush_order_fee(subtotal, rush_order_level)
        
        # Get regional pricing
        regional_config = self.regional_pricing.get(region, self.regional_pricing["central_california"])
        delivery_zone = regional_config.delivery_zone
        
        # Calculate delivery fees
        delivery_fee = self.calculate_delivery_fees(subtotal, delivery_zone)
        
        # Apply regional adjustments
        regional_adjustments = subtotal * (regional_config.adjustment_factor - 1.0)
        
        # Calculate tax
        tax_amount = (subtotal + regional_adjustments) * regional_config.local_tax_rate
        
        # Calculate total
        total = (
            subtotal +
            markup_amount +
            rush_order_fee +
            delivery_fee +
            regional_adjustments +
            tax_amount -
            volume_discount_amount
        )
        
        # Calculate delivery estimate
        estimated_delivery_days = self._estimate_delivery_time(line_items, rush_order_level)
        
        # Generate notes
        notes = []
        if volume_discount_amount > 0:
            notes.append(f"Volume discount applied: {volume_discount_percentage*100:.1f}%")
        if rush_order_fee > 0:
            notes.append(f"Rush order fee: {rush_order_level.value*100:.1f}%")
        if regional_adjustments != 0:
            notes.append(f"Regional adjustment: {regional_adjustments:+.2f}")
        
        result = PricingResult(
            line_items=line_items,
            subtotal=subtotal,
            volume_discount_amount=volume_discount_amount,
            volume_discount_percentage=volume_discount_percentage,
            rush_order_fee=rush_order_fee,
            rush_order_level=rush_order_level,
            delivery_fee=delivery_fee,
            delivery_zone=delivery_zone,
            regional_adjustments=regional_adjustments,
            tax_amount=tax_amount,
            total=total,
            pricing_confidence=base_pricing["pricing_confidence"],
            estimated_delivery_days=estimated_delivery_days,
            notes=notes
        )
        
        self.logger.info(f"Complete pricing calculated: ${total:.2f}")
        return result
    
    def _calculate_bulk_discount(self, item: LineItem) -> float:
        """Calculate bulk discount for an item"""
        if item.quantity >= item.min_order_quantity * 5:
            return 0.10  # 10% for 5x minimum
        elif item.quantity >= item.min_order_quantity * 3:
            return 0.07  # 7% for 3x minimum
        elif item.quantity >= item.min_order_quantity * 2:
            return 0.05  # 5% for 2x minimum
        return 0.0
    
    def _calculate_pricing_confidence(self, item: LineItem) -> float:
        """Calculate pricing confidence based on historical data"""
        if not self.pricing_history:
            return 0.8  # Default confidence
        
        # Find historical prices for this item
        historical_prices = [
            h.unit_price for h in self.pricing_history
            if h.item_id == item.item_id and h.date > datetime.now() - timedelta(days=90)
        ]
        
        if not historical_prices:
            return 0.7  # No recent history
        
        # Calculate confidence based on price stability
        mean_price = statistics.mean(historical_prices)
        std_dev = statistics.stdev(historical_prices) if len(historical_prices) > 1 else 0
        
        if std_dev == 0:
            return 0.95  # Very stable pricing
        
        # Calculate coefficient of variation
        cv = std_dev / mean_price if mean_price > 0 else 1.0
        
        # Higher CV means lower confidence
        confidence = max(0.5, 1.0 - cv)
        return confidence
    
    def _calculate_rush_order_fee(self, subtotal: float, rush_level: RushOrderLevel) -> float:
        """Calculate rush order fee"""
        return subtotal * rush_level.value
    
    def _calculate_fuel_surcharge(self, delivery_zone: DeliveryZone) -> float:
        """Calculate fuel surcharge based on current market conditions"""
        # This would typically fetch current fuel prices from an API
        # For now, use estimated values
        base_fuel_surcharge = {
            DeliveryZone.LOCAL: 15.0,
            DeliveryZone.REGIONAL: 35.0,
            DeliveryZone.STATEWIDE: 75.0,
            DeliveryZone.INTERSTATE: 120.0,
            DeliveryZone.REMOTE: 200.0
        }
        return base_fuel_surcharge.get(delivery_zone, 0.0)
    
    def _estimate_delivery_time(self, line_items: List[LineItem], rush_level: RushOrderLevel) -> int:
        """Estimate delivery time based on items and rush level"""
        if not line_items:
            return 0
        
        # Calculate base delivery time
        max_lead_time = max(item.lead_time_days for item in line_items)
        
        # Apply rush order adjustments
        rush_multipliers = {
            RushOrderLevel.STANDARD: 1.0,
            RushOrderLevel.EXPEDITED: 0.7,
            RushOrderLevel.URGENT: 0.5,
            RushOrderLevel.CRITICAL: 0.3
        }
        
        estimated_days = max_lead_time * rush_multipliers.get(rush_level, 1.0)
        return max(1, int(estimated_days))  # Minimum 1 day
    
    def _is_quantity_related_to_term(self, quantity: ExtractedQuantity, term: TermMatch) -> bool:
        """Check if a quantity is related to a specific term"""
        # Simple proximity check - could be enhanced with more sophisticated NLP
        return (
            quantity.page_number == term.page_number and
            abs(quantity.line_number - term.line_number) <= 5 if quantity.line_number and term.line_number else True
        )
    
    def _calculate_lumber_estimation_confidence(self, analysis: CalTransAnalysisResult) -> float:
        """Calculate confidence in lumber estimation"""
        if not analysis.terminology_found:
            return 0.0
        
        # Count formwork and lumber terms
        formwork_count = len([
            term for term in analysis.terminology_found
            if "formwork" in term.term.lower() or "forming" in term.term.lower()
        ])
        
        lumber_count = len([
            term for term in analysis.terminology_found
            if any(keyword in term.term.lower() for keyword in [
                "lumber", "wood", "timber", "board", "plywood", "osb"
            ])
        ])
        
        # Calculate confidence based on term coverage
        total_relevant_terms = formwork_count + lumber_count
        confidence = min(1.0, total_relevant_terms / 10.0)  # Scale to 0-1
        
        return confidence
    
    def _get_lumber_price(self, size: str) -> float:
        """Get current lumber price for given size"""
        # This would typically fetch from a pricing API
        # For now, use estimated prices
        prices = {
            "2x4": 8.50,
            "2x6": 12.00,
            "2x8": 18.00,
            "2x10": 24.00,
            "2x12": 32.00,
            "4x4": 15.00,
            "4x6": 28.00,
            "6x6": 45.00
        }
        return prices.get(size, 10.00)  # Default price
    
    def add_pricing_history(self, history_entry: PricingHistory) -> None:
        """Add a new pricing history entry"""
        self.pricing_history.append(history_entry)
        self.logger.info(f"Added pricing history for item {history_entry.item_id}")
    
    def get_pricing_trends(self, item_id: str, days: int = 90) -> Dict[str, Any]:
        """Get pricing trends for a specific item"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        relevant_history = [
            h for h in self.pricing_history
            if h.item_id == item_id and h.date >= cutoff_date
        ]
        
        if not relevant_history:
            return {"trend": "no_data", "confidence": 0.0}
        
        prices = [h.unit_price for h in relevant_history]
        dates = [h.date for h in relevant_history]
        
        # Calculate trend
        if len(prices) >= 2:
            # Simple linear trend calculation
            x_values = [(d - dates[0]).days for d in dates]
            y_values = prices
            
            # Calculate slope (price change per day)
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                trend_percentage = (slope * 30) / statistics.mean(prices) * 100  # Monthly trend
                
                if trend_percentage > 5:
                    trend = "increasing"
                elif trend_percentage < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                trend_percentage = 0.0
        else:
            trend = "insufficient_data"
            trend_percentage = 0.0
        
        return {
            "trend": trend,
            "trend_percentage": trend_percentage,
            "data_points": len(relevant_history),
            "average_price": statistics.mean(prices),
            "price_range": max(prices) - min(prices),
            "confidence": min(1.0, len(relevant_history) / 10.0)
        }
    
    def validate_pricing(self, pricing_result: PricingResult) -> ValidationResult:
        """Validate pricing calculations"""
        issues = []
        
        # Check for negative values
        if pricing_result.subtotal < 0:
            issues.append("Subtotal cannot be negative")
        
        if pricing_result.total < 0:
            issues.append("Total cannot be negative")
        
        # Check for excessive markups
        if pricing_result.subtotal > 0:
            markup_ratio = (pricing_result.total - pricing_result.subtotal) / pricing_result.subtotal
            if markup_ratio > 1.0:  # More than 100% markup
                issues.append("Markup appears excessive (>100%)")
        
        # Check pricing confidence
        if pricing_result.pricing_confidence < self.pricing_confidence_threshold:
            issues.append(f"Low pricing confidence: {pricing_result.pricing_confidence:.2f}")
        
        if issues:
            return ValidationResult(False, ValidationLevel.WARNING, "; ".join(issues))
        else:
            return ValidationResult(True, ValidationLevel.INFO, "Pricing validation passed")


def create_pricing_calculator() -> PricingCalculator:
    """Factory function to create a PricingCalculator instance"""
    return PricingCalculator()


# Example usage and testing functions
def test_pricing_calculator():
    """Test the PricingCalculator functionality"""
    calculator = PricingCalculator()
    
    # Create sample line items
    line_items = [
        LineItem(
            item_id="LUM001",
            description="2x4 Dimensional Lumber",
            quantity=100.0,
            unit="EA",
            base_unit_price=8.50,
            category="lumber",
            supplier="Whitecap",
            lead_time_days=7,
            bulk_pricing_available=True,
            min_order_quantity=50
        ),
        LineItem(
            item_id="PLY001",
            description="3/4\" CDX Plywood",
            quantity=25.0,
            unit="EA",
            base_unit_price=45.00,
            category="plywood",
            supplier="Whitecap",
            lead_time_days=10,
            bulk_pricing_available=True,
            min_order_quantity=10
        )
    ]
    
    # Calculate complete pricing
    result = calculator.calculate_complete_pricing(
        line_items=line_items,
        region="central_california",
        rush_order_level=RushOrderLevel.EXPEDITED,
        markup_percentage=0.25
    )
    
    print(f"Complete pricing result:")
    print(f"Subtotal: ${result.subtotal:.2f}")
    print(f"Volume discount: ${result.volume_discount_amount:.2f}")
    print(f"Rush order fee: ${result.rush_order_fee:.2f}")
    print(f"Delivery fee: ${result.delivery_fee:.2f}")
    print(f"Total: ${result.total:.2f}")
    print(f"Estimated delivery: {result.estimated_delivery_days} days")
    print(f"Pricing confidence: {result.pricing_confidence:.2f}")


if __name__ == "__main__":
    test_pricing_calculator() 