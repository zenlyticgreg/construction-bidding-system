"""
Unit tests for WhitecapCatalogExtractor

Comprehensive test suite covering:
- PDF processing capabilities
- Product categorization
- Data validation
- Error handling
- Performance metrics
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import json

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.extractors.whitecap_extractor import (
    WhitecapCatalogExtractor,
    ProductData,
    ProductCategory,
    ExtractionPriority,
    ExtractionConfig,
    extract_whitecap_catalog,
    extract_whitecap_sections
)


class TestWhitecapCatalogExtractor:
    """Test suite for WhitecapCatalogExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Create a basic extractor instance for testing"""
        config = ExtractionConfig(
            start_page=1,
            end_page=10,
            min_confidence_score=0.5,
            enable_progress_tracking=False,
            enable_validation=True
        )
        return WhitecapCatalogExtractor(config)
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing"""
        return """
        PRODUCT NO.    SKU         SIZE        DESCRIPTION                    PRICE
        WCP-001       WC001       2x4x8       Standard 2x4 Lumber            $5.99
        WCP-002       WC002       4x8x3/4     Plywood Sheathing              $12.50
        WCP-003       WC003       1/2"x8"     Concrete Form Tie              $0.85
        WCP-004       WC004       6"x6"       Concrete Form Spacer           $1.25
        WCP-005       WC005       2x6x12      Dimensional Lumber             $8.75
        """
    
    @pytest.fixture
    def sample_table_data(self):
        """Sample table data for testing"""
        return [
            ["PRODUCT NO.", "SKU", "SIZE", "DESCRIPTION", "PRICE"],
            ["WCP-001", "WC001", "2x4x8", "Standard 2x4 Lumber", "$5.99"],
            ["WCP-002", "WC002", "4x8x3/4", "Plywood Sheathing", "$12.50"],
            ["WCP-003", "WC003", "1/2\"x8\"", "Concrete Form Tie", "$0.85"],
            ["WCP-004", "WC004", "6\"x6\"", "Concrete Form Spacer", "$1.25"],
            ["WCP-005", "WC005", "2x6x12", "Dimensional Lumber", "$8.75"]
        ]
    
    @pytest.fixture
    def sample_product_data(self):
        """Sample product data for testing"""
        return ProductData(
            sku="WC001",
            product_name="Standard 2x4 Lumber",
            description="Standard 2x4 Lumber for construction",
            size="2x4x8",
            unit="EA",
            price=5.99,
            category=ProductCategory.LUMBER,
            priority=ExtractionPriority.HIGH,
            page_number=1,
            section="lumber",
            construction_relevance="high",
            confidence_score=0.95
        )

    def test_extractor_initialization(self, extractor):
        """Test extractor initialization with config"""
        assert extractor.config.start_page == 1
        assert extractor.config.end_page == 10
        assert extractor.config.min_confidence_score == 0.5
        assert extractor.config.enable_progress_tracking is False
        assert extractor.config.enable_validation is True
        assert extractor.logger is not None

    def test_default_config_initialization(self):
        """Test extractor initialization with default config"""
        extractor = WhitecapCatalogExtractor()
        assert extractor.config.start_page == 1
        assert extractor.config.end_page == 868
        assert extractor.config.min_confidence_score == 0.7
        assert extractor.config.enable_progress_tracking is True

    def test_setup_logger(self, extractor):
        """Test logger setup"""
        logger = extractor._setup_logger()
        assert logger is not None
        assert logger.name == "WhitecapCatalogExtractor"
        assert logger.level <= 20  # INFO level or lower

    @patch('src.extractors.whitecap_extractor.json.load')
    def test_load_catalog_sections(self, mock_json_load, extractor):
        """Test loading catalog sections from JSON"""
        mock_sections = {
            "concrete_forming": {"start_page": 10, "end_page": 50},
            "lumber": {"start_page": 51, "end_page": 100}
        }
        mock_json_load.return_value = mock_sections
        
        sections = extractor._load_catalog_sections()
        assert sections == mock_sections
        mock_json_load.assert_called_once()

    def test_setup_table_patterns(self, extractor):
        """Test table pattern setup"""
        patterns = extractor._setup_table_patterns()
        assert isinstance(patterns, dict)
        assert "product_no" in patterns
        assert "sku" in patterns
        assert "size" in patterns
        assert "description" in patterns
        assert "price" in patterns
        
        # Test pattern matching
        test_text = "PRODUCT NO. SKU SIZE DESCRIPTION PRICE"
        assert patterns["product_no"].search(test_text) is not None

    def test_setup_text_patterns(self, extractor):
        """Test text pattern setup"""
        patterns = extractor._setup_text_patterns()
        assert isinstance(patterns, dict)
        assert "product_line" in patterns
        assert "sku_pattern" in patterns
        assert "price_pattern" in patterns
        
        # Test pattern matching
        test_line = "WCP-001 WC001 2x4x8 Standard 2x4 Lumber $5.99"
        assert patterns["product_line"].search(test_line) is not None

    def test_setup_category_keywords(self, extractor):
        """Test category keyword setup"""
        keywords = extractor._setup_category_keywords()
        assert isinstance(keywords, dict)
        assert ProductCategory.FORMWORK in keywords
        assert ProductCategory.LUMBER in keywords
        assert ProductCategory.HARDWARE in keywords
        
        # Test keyword matching
        lumber_keywords = keywords[ProductCategory.LUMBER]
        assert "lumber" in lumber_keywords
        assert "plywood" in lumber_keywords

    @patch('src.extractors.whitecap_extractor.pdfplumber.open')
    def test_extract_catalog_data(self, mock_pdf_open, extractor, sample_pdf_content):
        """Test catalog data extraction from PDF"""
        # Mock PDF pages
        mock_page = Mock()
        mock_page.extract_text.return_value = sample_pdf_content
        mock_page.extract_tables.return_value = []
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page] * 5
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Test extraction
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"fake pdf content")
            tmp_file_path = tmp_file.name
        
        try:
            result = extractor.extract_catalog_data(tmp_file_path)
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)

    def test_extract_products_from_table(self, extractor, sample_table_data):
        """Test product extraction from table data"""
        products = extractor.extract_products_from_table(sample_table_data, 1)
        
        assert isinstance(products, list)
        assert len(products) == 5  # 5 products in sample data
        
        # Check first product
        first_product = products[0]
        assert first_product.sku == "WC001"
        assert first_product.product_name == "Standard 2x4 Lumber"
        assert first_product.size == "2x4x8"
        assert first_product.price == 5.99
        assert first_product.page_number == 1

    def test_extract_products_from_text(self, extractor, sample_pdf_content):
        """Test product extraction from text content"""
        products = extractor.extract_products_from_text(sample_pdf_content, 1)
        
        assert isinstance(products, list)
        assert len(products) > 0
        
        # Check that products have required fields
        for product in products:
            assert product.sku is not None
            assert product.product_name is not None
            assert product.description is not None
            assert product.size is not None
            assert product.page_number == 1

    def test_create_product_from_row(self, extractor):
        """Test creating product from table row"""
        row = ["WCP-001", "WC001", "2x4x8", "Standard 2x4 Lumber", "$5.99"]
        column_map = {
            "product_no": 0,
            "sku": 1,
            "size": 2,
            "description": 3,
            "price": 4
        }
        
        product = extractor._create_product_from_row(row, column_map, 1)
        
        assert product is not None
        assert product.sku == "WC001"
        assert product.product_name == "Standard 2x4 Lumber"
        assert product.size == "2x4x8"
        assert product.price == 5.99
        assert product.page_number == 1

    def test_create_product_from_invalid_row(self, extractor):
        """Test creating product from invalid row data"""
        row = ["", "", "", "", ""]  # Empty row
        column_map = {
            "product_no": 0,
            "sku": 1,
            "size": 2,
            "description": 3,
            "price": 4
        }
        
        product = extractor._create_product_from_row(row, column_map, 1)
        assert product is None

    def test_extract_product_from_line(self, extractor):
        """Test extracting product from text line"""
        line = "WCP-001 WC001 2x4x8 Standard 2x4 Lumber $5.99"
        
        product = extractor._extract_product_from_line(line, 1)
        
        assert product is not None
        assert product.sku == "WC001"
        assert product.product_name == "Standard 2x4 Lumber"
        assert product.size == "2x4x8"
        assert product.price == 5.99

    def test_extract_product_from_invalid_line(self, extractor):
        """Test extracting product from invalid text line"""
        line = "This is not a product line"
        
        product = extractor._extract_product_from_line(line, 1)
        assert product is None

    def test_categorize_product(self, extractor):
        """Test product categorization"""
        # Test lumber categorization
        category = extractor.categorize_product("WC001", "Standard 2x4 Lumber", None)
        assert category == ProductCategory.LUMBER
        
        # Test formwork categorization
        category = extractor.categorize_product("WC003", "Concrete Form Tie", None)
        assert category == ProductCategory.FORMWORK
        
        # Test hardware categorization
        category = extractor.categorize_product("WC010", "Steel Bolt", None)
        assert category == ProductCategory.HARDWARE
        
        # Test unknown categorization
        category = extractor.categorize_product("WC999", "Unknown Product", None)
        assert category == ProductCategory.UNKNOWN

    def test_determine_unit(self, extractor):
        """Test unit determination"""
        # Test linear feet
        unit = extractor.determine_unit("2x4x8", "Lumber")
        assert unit == "LF"
        
        # Test square feet
        unit = extractor.determine_unit("4x8", "Plywood")
        assert unit == "SF"
        
        # Test cubic yards
        unit = extractor.determine_unit("1 CY", "Concrete")
        assert unit == "CY"
        
        # Test each
        unit = extractor.determine_unit("6\"x6\"", "Spacer")
        assert unit == "EA"
        
        # Test default
        unit = extractor.determine_unit("", "Unknown")
        assert unit == "EA"

    def test_assess_construction_relevance(self, extractor):
        """Test construction relevance assessment"""
        # Test high relevance
        relevance = extractor.assess_construction_relevance(
            "Concrete form tie for bridge construction", 
            ProductCategory.FORMWORK
        )
        assert relevance == "high"
        
        # Test medium relevance
        relevance = extractor.assess_construction_relevance(
            "General purpose lumber", 
            ProductCategory.LUMBER
        )
        assert relevance == "medium"
        
        # Test low relevance
        relevance = extractor.assess_construction_relevance(
            "Office supplies", 
            ProductCategory.UNKNOWN
        )
        assert relevance == "low"

    def test_calculate_confidence_score(self, extractor):
        """Test confidence score calculation"""
        # Test high confidence
        score = extractor._calculate_confidence_score(
            "WC001", "Standard 2x4 Lumber", "2x4x8", 5.99
        )
        assert 0.8 <= score <= 1.0
        
        # Test medium confidence
        score = extractor._calculate_confidence_score(
            "WC001", "Lumber", "2x4x8", None
        )
        assert 0.5 <= score <= 0.8
        
        # Test low confidence
        score = extractor._calculate_confidence_score(
            "", "", "", None
        )
        assert 0.0 <= score <= 0.3

    def test_clean_dataframe(self, extractor):
        """Test dataframe cleaning"""
        # Create sample dataframe with issues
        data = {
            'sku': ['WC001', 'WC002', '', 'WC004', 'WC005'],
            'product_name': ['Lumber', 'Plywood', 'Invalid', 'Spacer', ''],
            'price': [5.99, 12.50, None, 1.25, 8.75],
            'category': ['lumber', 'lumber', 'unknown', 'formwork', 'lumber']
        }
        df = pd.DataFrame(data)
        
        cleaned_df = extractor.clean_dataframe(df)
        
        assert len(cleaned_df) < len(df)  # Should remove invalid rows
        assert cleaned_df['sku'].notna().all()  # No empty SKUs
        assert cleaned_df['product_name'].notna().all()  # No empty names
        assert cleaned_df['price'].notna().all()  # No empty prices

    def test_export_to_csv(self, extractor):
        """Test CSV export functionality"""
        # Create sample dataframe
        data = {
            'sku': ['WC001', 'WC002'],
            'product_name': ['Lumber', 'Plywood'],
            'price': [5.99, 12.50]
        }
        df = pd.DataFrame(data)
        
        # Test export
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            extractor.export_to_csv(df, output_path)
            assert Path(output_path).exists()
            
            # Verify content
            exported_df = pd.read_csv(output_path)
            assert len(exported_df) == 2
            assert exported_df['sku'].iloc[0] == 'WC001'
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_get_extraction_stats(self, extractor):
        """Test extraction statistics"""
        # Mock some extraction data
        extractor.total_products = 100
        extractor.valid_products = 95
        extractor.invalid_products = 5
        extractor.processing_time = 30.5
        
        stats = extractor.get_extraction_stats()
        
        assert stats['total_products'] == 100
        assert stats['valid_products'] == 95
        assert stats['invalid_products'] == 5
        assert stats['success_rate'] == 0.95
        assert stats['processing_time'] == 30.5

    @patch('src.extractors.whitecap_extractor.pdfplumber.open')
    def test_extract_by_sections(self, mock_pdf_open, extractor):
        """Test extraction by specific sections"""
        # Mock PDF
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample content"
        mock_page.extract_tables.return_value = []
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page] * 3
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        sections_config = {
            "concrete_forming": {"start_page": 1, "end_page": 2},
            "lumber": {"start_page": 3, "end_page": 3}
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"fake pdf content")
            tmp_file_path = tmp_file.name
        
        try:
            result = extractor.extract_by_sections(tmp_file_path, sections_config)
            assert isinstance(result, pd.DataFrame)
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)

    def test_error_handling_invalid_pdf(self, extractor):
        """Test error handling for invalid PDF"""
        with pytest.raises(Exception):
            extractor.extract_catalog_data("nonexistent_file.pdf")

    def test_error_handling_empty_pdf(self, extractor):
        """Test error handling for empty PDF"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"")
            tmp_file_path = tmp_file.name
        
        try:
            with pytest.raises(Exception):
                extractor.extract_catalog_data(tmp_file_path)
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)

    def test_product_data_validation(self, sample_product_data):
        """Test ProductData validation"""
        assert sample_product_data.sku == "WC001"
        assert sample_product_data.product_name == "Standard 2x4 Lumber"
        assert sample_product_data.price == 5.99
        assert sample_product_data.category == ProductCategory.LUMBER
        assert sample_product_data.confidence_score == 0.95
        assert isinstance(sample_product_data.extracted_at, datetime)

    def test_extraction_config_validation(self):
        """Test ExtractionConfig validation"""
        config = ExtractionConfig(
            start_page=1,
            end_page=100,
            min_confidence_score=0.8,
            enable_progress_tracking=True,
            enable_validation=True
        )
        
        assert config.start_page == 1
        assert config.end_page == 100
        assert config.min_confidence_score == 0.8
        assert config.enable_progress_tracking is True
        assert config.enable_validation is True
        assert "concrete_forming" in config.priority_sections


class TestExtractorFunctions:
    """Test suite for extractor utility functions"""
    
    @patch('src.extractors.whitecap_extractor.WhitecapCatalogExtractor')
    def test_extract_whitecap_catalog(self, mock_extractor_class):
        """Test extract_whitecap_catalog function"""
        mock_extractor = Mock()
        mock_extractor.extract_catalog_data.return_value = pd.DataFrame({'test': [1, 2, 3]})
        mock_extractor_class.return_value = mock_extractor
        
        result = extract_whitecap_catalog("test.pdf")
        
        assert isinstance(result, pd.DataFrame)
        mock_extractor.extract_catalog_data.assert_called_once_with("test.pdf")

    @patch('src.extractors.whitecap_extractor.WhitecapCatalogExtractor')
    def test_extract_whitecap_sections(self, mock_extractor_class):
        """Test extract_whitecap_sections function"""
        mock_extractor = Mock()
        mock_extractor.extract_by_sections.return_value = pd.DataFrame({'test': [1, 2, 3]})
        mock_extractor_class.return_value = mock_extractor
        
        sections = ["concrete_forming", "lumber"]
        result = extract_whitecap_sections("test.pdf", sections)
        
        assert isinstance(result, pd.DataFrame)
        mock_extractor.extract_by_sections.assert_called_once()


class TestExtractorPerformance:
    """Test suite for extractor performance"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        extractor = WhitecapCatalogExtractor()
        
        # Create large sample data
        large_data = []
        for i in range(1000):
            large_data.append({
                'sku': f'WC{i:03d}',
                'product_name': f'Product {i}',
                'price': 10.0 + i * 0.1
            })
        
        df = pd.DataFrame(large_data)
        
        # Test processing time
        import time
        start_time = time.time()
        cleaned_df = extractor.clean_dataframe(df)
        processing_time = time.time() - start_time
        
        assert processing_time < 5.0  # Should process in under 5 seconds
        assert len(cleaned_df) == 1000  # Should maintain all valid records

    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        extractor = WhitecapCatalogExtractor()
        
        # Create memory-intensive dataset
        large_text = "Sample product data " * 10000
        
        # Test memory efficiency
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large text
        products = extractor.extract_products_from_text(large_text, 1)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        assert memory_increase < 100  # Should not increase memory by more than 100MB


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 