"""
Unit tests for CalTrans Bidding System

Comprehensive test suite covering:
- Bid generation workflow
- Pricing calculations
- Product matching accuracy
- Excel output validation
- Error handling
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import json

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.bidding.bid_engine import (
    CalTransBiddingEngine,
    BidItem,
    BidConfiguration,
    BidResult,
    generate_bid,
    calculate_pricing
)
from src.utils.excel_generator import (
    ExcelBidGenerator,
    generate_excel_bid,
    format_bid_sheet
)


class TestCalTransBiddingEngine:
    """Test suite for CalTransBiddingEngine"""
    
    @pytest.fixture
    def bid_engine(self):
        """Create a basic bid engine instance for testing"""
        return CalTransBiddingEngine()
    
    @pytest.fixture
    def sample_bid_config(self):
        """Sample bid configuration for testing"""
        return BidConfiguration(
            project_name="Test Bridge Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=15.0,
            overhead_rate=10.0,
            profit_margin=8.0,
            contingency_rate=5.0,
            tax_rate=8.25,
            currency="USD"
        )
    
    @pytest.fixture
    def sample_bid_items(self):
        """Sample bid items for testing"""
        return [
            BidItem(
                item_number="001",
                description="Concrete, Class A, 3000 PSI",
                quantity=100.0,
                unit="CY",
                unit_price=150.00,
                category="Materials",
                notes="Standard concrete mix"
            ),
            BidItem(
                item_number="002",
                description="Reinforcing Steel, Grade 60",
                quantity=5000.0,
                unit="LB",
                unit_price=0.85,
                category="Materials",
                notes="Deformed bars"
            ),
            BidItem(
                item_number="003",
                description="Excavation, Common",
                quantity=200.0,
                unit="CY",
                unit_price=25.00,
                category="Earthwork",
                notes="Unclassified excavation"
            ),
            BidItem(
                item_number="004",
                description="Formwork Installation",
                quantity=500.0,
                unit="SF",
                unit_price=12.50,
                category="Labor",
                notes="Wood formwork"
            )
        ]
    
    @pytest.fixture
    def sample_catalog_data(self):
        """Sample catalog data for testing"""
        return pd.DataFrame({
            'sku': ['WC001', 'WC002', 'WC003', 'WC004'],
            'product_name': ['2x4 Lumber', 'Plywood', 'Form Tie', 'Spacer'],
            'price': [5.99, 12.50, 0.85, 1.25],
            'category': ['lumber', 'lumber', 'formwork', 'formwork'],
            'unit': ['LF', 'SF', 'EA', 'EA']
        })
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data for testing"""
        return {
            'terms': [
                {
                    'term': 'BALUSTER',
                    'category': 'safety',
                    'priority': 'high',
                    'confidence': 0.95
                },
                {
                    'term': 'TYPE_86H_RAIL',
                    'category': 'safety',
                    'priority': 'high',
                    'confidence': 0.90
                }
            ],
            'quantities': [
                {
                    'value': 2500.0,
                    'unit': 'SQFT',
                    'context': 'Bridge deck concrete'
                },
                {
                    'value': 1200.0,
                    'unit': 'LF',
                    'context': 'Formwork installation'
                },
                {
                    'value': 50.0,
                    'unit': 'EA',
                    'context': 'BALUSTER installation'
                }
            ]
        }

    def test_bid_engine_initialization(self, bid_engine):
        """Test bid engine initialization"""
        assert bid_engine is not None
        assert bid_engine.default_markup == 15.0
        assert bid_engine.default_tax_rate == 8.25
        assert bid_engine.currency_symbol == "$"

    def test_bid_configuration_validation(self, sample_bid_config):
        """Test bid configuration validation"""
        assert sample_bid_config.project_name == "Test Bridge Project"
        assert sample_bid_config.project_number == "04-123456"
        assert sample_bid_config.markup_percentage == 15.0
        assert sample_bid_config.overhead_rate == 10.0
        assert sample_bid_config.profit_margin == 8.0
        assert sample_bid_config.contingency_rate == 5.0
        assert sample_bid_config.tax_rate == 8.25
        assert sample_bid_config.currency == "USD"

    def test_bid_item_validation(self, sample_bid_items):
        """Test bid item validation"""
        for item in sample_bid_items:
            assert item.item_number is not None
            assert item.description is not None
            assert item.quantity > 0
            assert item.unit is not None
            assert item.unit_price >= 0
            assert item.category is not None

    def test_generate_bid_workflow(self, bid_engine, sample_bid_config, sample_bid_items):
        """Test complete bid generation workflow"""
        bid_result = bid_engine.generate_bid(sample_bid_config, sample_bid_items)
        
        assert isinstance(bid_result, BidResult)
        assert bid_result.config == sample_bid_config
        assert bid_result.items == sample_bid_items
        assert bid_result.subtotal > 0
        assert bid_result.markup_amount > 0
        assert bid_result.overhead_amount > 0
        assert bid_result.profit_amount > 0
        assert bid_result.contingency_amount > 0
        assert bid_result.tax_amount > 0
        assert bid_result.grand_total > 0
        assert bid_result.generated_at is not None

    def test_calculate_pricing(self, bid_engine, sample_bid_items, sample_bid_config):
        """Test pricing calculations"""
        pricing = bid_engine.calculate_pricing(sample_bid_items, sample_bid_config)
        
        assert isinstance(pricing, dict)
        assert pricing['subtotal'] > 0
        assert pricing['markup_amount'] > 0
        assert pricing['overhead_amount'] > 0
        assert pricing['profit_amount'] > 0
        assert pricing['contingency_amount'] > 0
        assert pricing['tax_amount'] > 0
        assert pricing['grand_total'] > 0
        
        # Verify calculations
        expected_subtotal = sum(item.quantity * item.unit_price for item in sample_bid_items)
        assert abs(pricing['subtotal'] - expected_subtotal) < 0.01
        
        expected_markup = expected_subtotal * (sample_bid_config.markup_percentage / 100)
        assert abs(pricing['markup_amount'] - expected_markup) < 0.01

    def test_calculate_pricing_with_zero_markup(self, bid_engine, sample_bid_items):
        """Test pricing calculations with zero markup"""
        config = BidConfiguration(
            project_name="Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=0.0,
            overhead_rate=0.0,
            profit_margin=0.0,
            contingency_rate=0.0,
            tax_rate=0.0,
            currency="USD"
        )
        
        pricing = bid_engine.calculate_pricing(sample_bid_items, config)
        
        assert pricing['markup_amount'] == 0.0
        assert pricing['overhead_amount'] == 0.0
        assert pricing['profit_amount'] == 0.0
        assert pricing['contingency_amount'] == 0.0
        assert pricing['tax_amount'] == 0.0
        assert pricing['grand_total'] == pricing['subtotal']

    def test_calculate_pricing_with_high_markup(self, bid_engine, sample_bid_items):
        """Test pricing calculations with high markup"""
        config = BidConfiguration(
            project_name="Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=50.0,
            overhead_rate=20.0,
            profit_margin=15.0,
            contingency_rate=10.0,
            tax_rate=10.0,
            currency="USD"
        )
        
        pricing = bid_engine.calculate_pricing(sample_bid_items, config)
        
        assert pricing['markup_amount'] > 0
        assert pricing['overhead_amount'] > 0
        assert pricing['profit_amount'] > 0
        assert pricing['contingency_amount'] > 0
        assert pricing['tax_amount'] > 0
        assert pricing['grand_total'] > pricing['subtotal']

    def test_match_products_to_catalog(self, bid_engine, sample_bid_items, sample_catalog_data):
        """Test product matching to catalog"""
        matched_items = bid_engine.match_products_to_catalog(sample_bid_items, sample_catalog_data)
        
        assert isinstance(matched_items, list)
        assert len(matched_items) == len(sample_bid_items)
        
        for item in matched_items:
            assert item.catalog_match is not None
            assert item.matching_confidence >= 0.0
            assert item.matching_confidence <= 1.0

    def test_match_products_accuracy(self, bid_engine, sample_catalog_data):
        """Test product matching accuracy"""
        # Test exact matches
        exact_match_items = [
            BidItem(
                item_number="001",
                description="2x4 Lumber",
                quantity=100.0,
                unit="LF",
                unit_price=0.0,
                category="Materials"
            )
        ]
        
        matched_items = bid_engine.match_products_to_catalog(exact_match_items, sample_catalog_data)
        
        assert len(matched_items) == 1
        assert matched_items[0].catalog_match is not None
        assert matched_items[0].matching_confidence >= 0.8
        
        # Test partial matches
        partial_match_items = [
            BidItem(
                item_number="002",
                description="Wood lumber",
                quantity=100.0,
                unit="LF",
                unit_price=0.0,
                category="Materials"
            )
        ]
        
        matched_items = bid_engine.match_products_to_catalog(partial_match_items, sample_catalog_data)
        
        assert len(matched_items) == 1
        assert matched_items[0].matching_confidence >= 0.5

    def test_validate_bid_items(self, bid_engine, sample_bid_items):
        """Test bid item validation"""
        validation_results = bid_engine.validate_bid_items(sample_bid_items)
        
        assert isinstance(validation_results, list)
        assert len(validation_results) == len(sample_bid_items)
        
        for result in validation_results:
            assert result.item is not None
            assert result.is_valid is not None
            assert result.issues is not None
            assert result.recommendations is not None

    def test_validate_bid_items_with_invalid_data(self, bid_engine):
        """Test bid item validation with invalid data"""
        invalid_items = [
            BidItem(
                item_number="001",
                description="",
                quantity=0.0,
                unit="",
                unit_price=-10.0,
                category=""
            )
        ]
        
        validation_results = bid_engine.validate_bid_items(invalid_items)
        
        assert len(validation_results) == 1
        assert not validation_results[0].is_valid
        assert len(validation_results[0].issues) > 0

    def test_generate_bid_summary(self, bid_engine, sample_bid_config, sample_bid_items):
        """Test bid summary generation"""
        summary = bid_engine.generate_bid_summary(sample_bid_config, sample_bid_items)
        
        assert isinstance(summary, dict)
        assert "total_items" in summary
        assert "total_quantity" in summary
        assert "total_value" in summary
        assert "categories" in summary
        assert "project_info" in summary
        
        assert summary["total_items"] == len(sample_bid_items)
        assert summary["total_value"] > 0

    def test_error_handling_invalid_config(self, bid_engine, sample_bid_items):
        """Test error handling with invalid configuration"""
        with pytest.raises(Exception):
            bid_engine.generate_bid(None, sample_bid_items)

    def test_error_handling_empty_items(self, bid_engine, sample_bid_config):
        """Test error handling with empty items"""
        with pytest.raises(Exception):
            bid_engine.generate_bid(sample_bid_config, [])

    def test_error_handling_invalid_items(self, bid_engine, sample_bid_config):
        """Test error handling with invalid items"""
        invalid_items = [
            BidItem(
                item_number="001",
                description="Test",
                quantity=-100.0,  # Invalid negative quantity
                unit="CY",
                unit_price=150.00,
                category="Materials"
            )
        ]
        
        with pytest.raises(Exception):
            bid_engine.generate_bid(sample_bid_config, invalid_items)


class TestExcelBidGenerator:
    """Test suite for ExcelBidGenerator"""
    
    @pytest.fixture
    def excel_generator(self):
        """Create a basic Excel generator instance for testing"""
        return ExcelBidGenerator()
    
    @pytest.fixture
    def sample_bid_result(self, sample_bid_config, sample_bid_items):
        """Sample bid result for testing"""
        bid_engine = CalTransBiddingEngine()
        return bid_engine.generate_bid(sample_bid_config, sample_bid_items)

    def test_excel_generator_initialization(self, excel_generator):
        """Test Excel generator initialization"""
        assert excel_generator is not None
        assert excel_generator.default_format is not None
        assert excel_generator.currency_format is not None

    def test_generate_excel_bid(self, excel_generator, sample_bid_result):
        """Test Excel bid generation"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            result = excel_generator.generate_excel_bid(sample_bid_result, output_path)
            
            assert result is True
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
            
            # Verify Excel file can be read
            df = pd.read_excel(output_path, sheet_name='Bid Summary')
            assert len(df) > 0
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_format_bid_sheet(self, excel_generator, sample_bid_result):
        """Test bid sheet formatting"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Create basic Excel file
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df = pd.DataFrame({
                    'Item': [item.item_number for item in sample_bid_result.items],
                    'Description': [item.description for item in sample_bid_result.items],
                    'Quantity': [item.quantity for item in sample_bid_result.items],
                    'Unit': [item.unit for item in sample_bid_result.items],
                    'Unit Price': [item.unit_price for item in sample_bid_result.items],
                    'Total': [item.quantity * item.unit_price for item in sample_bid_result.items]
                })
                df.to_excel(writer, sheet_name='Bid Items', index=False)
            
            # Format the sheet
            excel_generator.format_bid_sheet(output_path, 'Bid Items')
            
            # Verify file still exists and is readable
            assert Path(output_path).exists()
            df = pd.read_excel(output_path, sheet_name='Bid Items')
            assert len(df) > 0
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_create_bid_summary_sheet(self, excel_generator, sample_bid_result):
        """Test bid summary sheet creation"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            excel_generator.create_bid_summary_sheet(sample_bid_result, output_path)
            
            assert Path(output_path).exists()
            
            # Verify summary sheet
            df = pd.read_excel(output_path, sheet_name='Bid Summary')
            assert len(df) > 0
            
            # Check for key summary information
            summary_text = df.to_string()
            assert "Project Name" in summary_text
            assert "Grand Total" in summary_text
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_create_bid_items_sheet(self, excel_generator, sample_bid_result):
        """Test bid items sheet creation"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            excel_generator.create_bid_items_sheet(sample_bid_result, output_path)
            
            assert Path(output_path).exists()
            
            # Verify items sheet
            df = pd.read_excel(output_path, sheet_name='Bid Items')
            assert len(df) == len(sample_bid_result.items)
            
            # Check columns
            expected_columns = ['Item', 'Description', 'Quantity', 'Unit', 'Unit Price', 'Total']
            for col in expected_columns:
                assert col in df.columns
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_create_pricing_breakdown_sheet(self, excel_generator, sample_bid_result):
        """Test pricing breakdown sheet creation"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            excel_generator.create_pricing_breakdown_sheet(sample_bid_result, output_path)
            
            assert Path(output_path).exists()
            
            # Verify breakdown sheet
            df = pd.read_excel(output_path, sheet_name='Pricing Breakdown')
            assert len(df) > 0
            
            # Check for pricing components
            breakdown_text = df.to_string()
            assert "Subtotal" in breakdown_text
            assert "Markup" in breakdown_text
            assert "Overhead" in breakdown_text
            assert "Profit" in breakdown_text
            assert "Tax" in breakdown_text
            assert "Grand Total" in breakdown_text
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_error_handling_invalid_bid_result(self, excel_generator):
        """Test error handling with invalid bid result"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            with pytest.raises(Exception):
                excel_generator.generate_excel_bid(None, output_path)
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_error_handling_invalid_output_path(self, excel_generator, sample_bid_result):
        """Test error handling with invalid output path"""
        with pytest.raises(Exception):
            excel_generator.generate_excel_bid(sample_bid_result, "/invalid/path/file.xlsx")


class TestBiddingFunctions:
    """Test suite for bidding utility functions"""
    
    def test_generate_bid_function(self, sample_bid_config, sample_bid_items):
        """Test generate_bid function"""
        result = generate_bid(sample_bid_config, sample_bid_items)
        
        assert isinstance(result, BidResult)
        assert result.config == sample_bid_config
        assert result.items == sample_bid_items
        assert result.grand_total > 0

    def test_calculate_pricing_function(self, sample_bid_items, sample_bid_config):
        """Test calculate_pricing function"""
        pricing = calculate_pricing(sample_bid_items, sample_bid_config)
        
        assert isinstance(pricing, dict)
        assert pricing['subtotal'] > 0
        assert pricing['grand_total'] > 0

    def test_generate_excel_bid_function(self, sample_bid_result):
        """Test generate_excel_bid function"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            result = generate_excel_bid(sample_bid_result, output_path)
            
            assert result is True
            assert Path(output_path).exists()
            
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_format_bid_sheet_function(self, sample_bid_result):
        """Test format_bid_sheet function"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Create basic Excel file
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df = pd.DataFrame({
                    'Item': [item.item_number for item in sample_bid_result.items],
                    'Description': [item.description for item in sample_bid_result.items],
                    'Quantity': [item.quantity for item in sample_bid_result.items],
                    'Unit': [item.unit for item in sample_bid_result.items],
                    'Unit Price': [item.unit_price for item in sample_bid_result.items],
                    'Total': [item.quantity * item.unit_price for item in sample_bid_result.items]
                })
                df.to_excel(writer, sheet_name='Bid Items', index=False)
            
            # Format the sheet
            format_bid_sheet(output_path, 'Bid Items')
            
            # Verify file still exists
            assert Path(output_path).exists()
            
        finally:
            Path(output_path).unlink(missing_ok=True)


class TestBiddingPerformance:
    """Test suite for bidding performance"""
    
    def test_large_bid_generation(self):
        """Test generation of large bids"""
        bid_engine = CalTransBiddingEngine()
        
        # Create large number of bid items
        large_items = []
        for i in range(1000):
            large_items.append(BidItem(
                item_number=f"{i+1:03d}",
                description=f"Item {i+1}",
                quantity=100.0 + i,
                unit="EA",
                unit_price=10.0 + i * 0.1,
                category="Materials"
            ))
        
        config = BidConfiguration(
            project_name="Large Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=15.0,
            overhead_rate=10.0,
            profit_margin=8.0,
            contingency_rate=5.0,
            tax_rate=8.25,
            currency="USD"
        )
        
        # Test processing time
        import time
        start_time = time.time()
        bid_result = bid_engine.generate_bid(config, large_items)
        processing_time = time.time() - start_time
        
        assert processing_time < 5.0  # Should process in under 5 seconds
        assert bid_result.grand_total > 0
        assert len(bid_result.items) == 1000

    def test_excel_generation_performance(self, sample_bid_result):
        """Test Excel generation performance"""
        excel_generator = ExcelBidGenerator()
        
        # Create large bid result
        large_items = []
        for i in range(500):
            large_items.append(BidItem(
                item_number=f"{i+1:03d}",
                description=f"Item {i+1}",
                quantity=100.0,
                unit="EA",
                unit_price=10.0,
                category="Materials"
            ))
        
        large_bid_result = BidResult(
            config=sample_bid_result.config,
            items=large_items,
            subtotal=sum(item.quantity * item.unit_price for item in large_items),
            markup_amount=0,
            overhead_amount=0,
            profit_amount=0,
            contingency_amount=0,
            tax_amount=0,
            grand_total=sum(item.quantity * item.unit_price for item in large_items),
            generated_at=datetime.now()
        )
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Test processing time
            import time
            start_time = time.time()
            result = excel_generator.generate_excel_bid(large_bid_result, output_path)
            processing_time = time.time() - start_time
            
            assert processing_time < 10.0  # Should process in under 10 seconds
            assert result is True
            assert Path(output_path).exists()
            
        finally:
            Path(output_path).unlink(missing_ok=True)


class TestBiddingEdgeCases:
    """Test suite for bidding edge cases"""
    
    def test_zero_quantity_items(self):
        """Test handling of zero quantity items"""
        bid_engine = CalTransBiddingEngine()
        
        zero_items = [
            BidItem(
                item_number="001",
                description="Test Item",
                quantity=0.0,
                unit="EA",
                unit_price=10.0,
                category="Materials"
            )
        ]
        
        config = BidConfiguration(
            project_name="Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=15.0,
            overhead_rate=10.0,
            profit_margin=8.0,
            contingency_rate=5.0,
            tax_rate=8.25,
            currency="USD"
        )
        
        bid_result = bid_engine.generate_bid(config, zero_items)
        
        assert bid_result.subtotal == 0.0
        assert bid_result.grand_total == 0.0

    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        bid_engine = CalTransBiddingEngine()
        
        large_items = [
            BidItem(
                item_number="001",
                description="Large Item",
                quantity=1000000.0,
                unit="EA",
                unit_price=1000000.0,
                category="Materials"
            )
        ]
        
        config = BidConfiguration(
            project_name="Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=15.0,
            overhead_rate=10.0,
            profit_margin=8.0,
            contingency_rate=5.0,
            tax_rate=8.25,
            currency="USD"
        )
        
        bid_result = bid_engine.generate_bid(config, large_items)
        
        assert bid_result.subtotal > 0
        assert bid_result.grand_total > bid_result.subtotal
        assert not np.isinf(bid_result.grand_total)
        assert not np.isnan(bid_result.grand_total)

    def test_special_characters_in_descriptions(self):
        """Test handling of special characters in descriptions"""
        bid_engine = CalTransBiddingEngine()
        
        special_items = [
            BidItem(
                item_number="001",
                description="Item with special chars: @#$%^&*()_+{}|:<>?[]\\;'\",./",
                quantity=100.0,
                unit="EA",
                unit_price=10.0,
                category="Materials"
            )
        ]
        
        config = BidConfiguration(
            project_name="Test Project",
            project_number="04-123456",
            contract_type="Construction",
            bid_date=datetime.now().date(),
            completion_date=(datetime.now() + timedelta(days=365)).date(),
            markup_percentage=15.0,
            overhead_rate=10.0,
            profit_margin=8.0,
            contingency_rate=5.0,
            tax_rate=8.25,
            currency="USD"
        )
        
        bid_result = bid_engine.generate_bid(config, special_items)
        
        assert bid_result.subtotal > 0
        assert bid_result.grand_total > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 