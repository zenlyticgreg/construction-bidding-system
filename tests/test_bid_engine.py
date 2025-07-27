"""
Test suite for CalTrans Bidding Engine

This module provides comprehensive tests for the CalTransBiddingEngine class,
including unit tests for all major functionality and integration tests.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bidding.bid_engine import (
    CalTransBiddingEngine, 
    BidLineItem, 
    PricingSummary, 
    BidPackage,
    WasteFactor,
    PricingConfig
)


class TestCalTransBiddingEngine(unittest.TestCase):
    """Test cases for CalTransBiddingEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = CalTransBiddingEngine()
        
        # Mock data for testing
        self.mock_term_data = {
            "term": "BALUSTER",
            "category": "bridge_barrier",
            "context": "baluster installation for bridge railing"
        }
        
        self.mock_products = [
            {
                "product_id": "FW001",
                "product_name": "3/4\" CDX Plywood 4x8",
                "category": "formwork",
                "match_score": 85.0,
                "quality": "high",
                "price": 32.50,
                "estimated_price": None,
                "supplier": "Whitecap",
                "availability": True,
                "match_reason": "Exact match for 'plywood' (score: 85.0)"
            }
        ]
        
        self.mock_line_items = [
            BidLineItem(
                item_number="001",
                description="BALUSTER - bridge_barrier",
                caltrans_term="BALUSTER",
                quantity=100.0,
                unit="EA",
                unit_price=25.0,
                total_price=2500.0,
                product_matches=self.mock_products,
                waste_factor=0.10,
                markup_percentage=0.20
            )
        ]
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.logger)
        self.assertIsNotNone(self.engine.matching_strategies)
        self.assertIsNotNone(self.engine.quantity_factors)
    
    def test_matching_strategies(self):
        """Test product matching strategies"""
        strategies = self.engine.matching_strategies
        
        # Test specific strategies
        self.assertIn("BALUSTER", strategies)
        self.assertIn("BLOCKOUT", strategies)
        self.assertIn("STAMPED_CONCRETE", strategies)
        self.assertIn("RETAINING_WALL", strategies)
        self.assertIn("EROSION_CONTROL", strategies)
        
        # Test strategy content
        baluster_strategy = strategies["BALUSTER"]
        self.assertIn("concrete", baluster_strategy)
        self.assertIn("form", baluster_strategy)
        self.assertIn("plywood", baluster_strategy)
    
    def test_quantity_factors(self):
        """Test quantity calculation factors"""
        factors = self.engine.quantity_factors
        
        # Test specific factors
        self.assertIn("BALUSTER", factors)
        self.assertIn("FORMWORK", factors)
        self.assertIn("RETAINING_WALL", factors)
        
        # Test factor structure
        baluster_factor = factors["BALUSTER"]
        self.assertEqual(baluster_factor["base_factor"], 1.0)
        self.assertEqual(baluster_factor["unit"], "EA")
    
    def test_find_products_for_term(self):
        """Test product matching for terms"""
        # Mock the product matcher
        with patch.object(self.engine, 'product_matcher') as mock_matcher:
            mock_matcher.find_products_by_terms.return_value = self.mock_products
            
            products = self.engine.find_products_for_term(self.mock_term_data)
            
            # Verify the method was called
            mock_matcher.find_products_by_terms.assert_called_once()
            
            # Verify results
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0]["product_id"], "FW001")
    
    def test_calculate_quantity_needed(self):
        """Test quantity calculation"""
        from analyzers.caltrans_analyzer import ExtractedQuantity
        
        # Mock quantities
        quantities = [
            ExtractedQuantity(
                value=100.0, 
                unit="EA", 
                context="baluster installation", 
                page_number=1
            ),
            ExtractedQuantity(
                value=50.0, 
                unit="LF", 
                context="railing length", 
                page_number=1
            )
        ]
        
        # Test quantity calculation
        quantity = self.engine.calculate_quantity_needed(self.mock_term_data, quantities)
        
        # Should find the associated quantity (100 EA for baluster)
        self.assertEqual(quantity, 100.0)
    
    def test_calculate_pricing_summary(self):
        """Test pricing summary calculation"""
        pricing = self.engine.calculate_pricing_summary(self.mock_line_items)
        
        # Test basic calculations
        self.assertEqual(pricing["subtotal"], 2500.0)
        self.assertEqual(pricing["line_item_count"], 1)
        self.assertEqual(pricing["high_priority_items"], 1)  # high quality match
        
        # Test that all required fields are present
        required_fields = [
            "subtotal", "markup_amount", "delivery_fee", "waste_adjustments",
            "total", "line_item_count", "high_priority_items",
            "estimated_materials_cost", "estimated_labor_cost"
        ]
        
        for field in required_fields:
            self.assertIn(field, pricing)
    
    def test_determine_waste_factor(self):
        """Test waste factor determination"""
        # Test formwork terms
        waste_factor = self.engine._determine_waste_factor("FORMWORK", "formwork")
        self.assertEqual(waste_factor, PricingConfig.WASTE_FACTORS["formwork"])
        
        # Test lumber terms
        waste_factor = self.engine._determine_waste_factor("2X4", "lumber")
        self.assertEqual(waste_factor, PricingConfig.WASTE_FACTORS["lumber"])
        
        # Test hardware terms
        waste_factor = self.engine._determine_waste_factor("BOLT", "hardware")
        self.assertEqual(waste_factor, PricingConfig.WASTE_FACTORS["hardware"])
        
        # Test default
        waste_factor = self.engine._determine_waste_factor("UNKNOWN", "other")
        self.assertEqual(waste_factor, PricingConfig.WASTE_FACTORS["default"])
    
    def test_determine_unit(self):
        """Test unit determination"""
        # Test specific terms
        self.assertEqual(self.engine._determine_unit("BALUSTER"), "EA")
        self.assertEqual(self.engine._determine_unit("FORMWORK"), "SQFT")
        self.assertEqual(self.engine._determine_unit("RETAINING_WALL"), "SQFT")
        
        # Test content-based determination
        self.assertEqual(self.engine._determine_unit("WALL_FORM"), "SQFT")
        self.assertEqual(self.engine._determine_unit("RAIL_FENCE"), "LF")
        self.assertEqual(self.engine._determine_unit("CONCRETE_MIX"), "CY")
        
        # Test default
        self.assertEqual(self.engine._determine_unit("UNKNOWN"), "EA")
    
    def test_calculate_delivery_fee(self):
        """Test delivery fee calculation"""
        # Test percentage calculation
        fee = self.engine._calculate_delivery_fee(1000.0)
        expected_fee = 1000.0 * PricingConfig.DELIVERY_PERCENTAGE
        self.assertEqual(fee, expected_fee)
        
        # Test minimum fee
        fee = self.engine._calculate_delivery_fee(100.0)
        self.assertEqual(fee, PricingConfig.DELIVERY_MINIMUM)
    
    def test_save_and_load_bid(self):
        """Test bid save and load functionality"""
        bid_data = {
            "project_name": "Test Project",
            "project_number": "TEST-001",
            "line_items": [],
            "pricing_summary": {
                "subtotal": 1000.0,
                "total": 1200.0
            }
        }
        
        # Test save
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            self.engine.save_bid_to_file(bid_data, temp_file)
            
            # Verify file was created
            self.assertTrue(os.path.exists(temp_file))
            
            # Test load
            loaded_data = self.engine.load_bid_from_file(temp_file)
            
            # Verify data integrity
            self.assertEqual(loaded_data["project_name"], "Test Project")
            self.assertEqual(loaded_data["project_number"], "TEST-001")
            self.assertEqual(loaded_data["pricing_summary"]["subtotal"], 1000.0)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_generate_complete_bid_integration(self):
        """Test complete bid generation (integration test)"""
        # Mock the CalTrans analyzer
        with patch.object(self.engine, 'caltrans_analyzer') as mock_analyzer:
            # Create mock analysis result
            mock_result = Mock()
            mock_result.terminology_found = [
                Mock(term="BALUSTER", category="bridge_barrier", context="test", page_number=1)
            ]
            mock_result.quantities = [
                Mock(value=100.0, unit="EA", context="baluster", page_number=1)
            ]
            mock_result.high_priority_terms = 1
            mock_result.critical_alerts = 0
            
            mock_analyzer.analyze_pdf.return_value = mock_result
            
            # Mock product matcher
            with patch.object(self.engine, 'product_matcher') as mock_matcher:
                mock_matcher.find_products_by_terms.return_value = self.mock_products
                
                # Test bid generation
                bid_data = self.engine.generate_complete_bid(
                    "test.pdf",
                    "Test Project",
                    "TEST-001",
                    0.20
                )
                
                # Verify basic structure
                self.assertIn("project_name", bid_data)
                self.assertIn("project_number", bid_data)
                self.assertIn("line_items", bid_data)
                self.assertIn("pricing_summary", bid_data)
                
                # Verify project info
                self.assertEqual(bid_data["project_name"], "Test Project")
                self.assertEqual(bid_data["project_number"], "TEST-001")
                
                # Verify line items were generated
                self.assertGreater(len(bid_data["line_items"]), 0)
                
                # Verify pricing summary
                self.assertIn("total", bid_data["pricing_summary"])
                self.assertGreater(bid_data["pricing_summary"]["total"], 0)


class TestBidLineItem(unittest.TestCase):
    """Test cases for BidLineItem dataclass"""
    
    def test_bid_line_item_creation(self):
        """Test BidLineItem creation"""
        line_item = BidLineItem(
            item_number="001",
            description="Test Item",
            caltrans_term="BALUSTER",
            quantity=100.0,
            unit="EA",
            unit_price=25.0,
            total_price=2500.0
        )
        
        self.assertEqual(line_item.item_number, "001")
        self.assertEqual(line_item.description, "Test Item")
        self.assertEqual(line_item.caltrans_term, "BALUSTER")
        self.assertEqual(line_item.quantity, 100.0)
        self.assertEqual(line_item.unit, "EA")
        self.assertEqual(line_item.unit_price, 25.0)
        self.assertEqual(line_item.total_price, 2500.0)
        self.assertEqual(line_item.waste_factor, 0.08)  # default
        self.assertEqual(line_item.markup_percentage, 0.20)  # default


class TestPricingConfig(unittest.TestCase):
    """Test cases for PricingConfig"""
    
    def test_pricing_config_constants(self):
        """Test pricing configuration constants"""
        self.assertEqual(PricingConfig.DEFAULT_MARKUP, 0.20)
        self.assertEqual(PricingConfig.DELIVERY_PERCENTAGE, 0.03)
        self.assertEqual(PricingConfig.DELIVERY_MINIMUM, 150.00)
        
        # Test waste factors
        self.assertEqual(PricingConfig.WASTE_FACTORS["formwork"], WasteFactor.FORMWORK.value)
        self.assertEqual(PricingConfig.WASTE_FACTORS["lumber"], WasteFactor.LUMBER.value)
        self.assertEqual(PricingConfig.WASTE_FACTORS["hardware"], WasteFactor.HARDWARE.value)
        self.assertEqual(PricingConfig.WASTE_FACTORS["specialty"], WasteFactor.SPECIALTY.value)


if __name__ == "__main__":
    unittest.main() 