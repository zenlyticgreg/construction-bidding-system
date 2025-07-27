"""
Pytest configuration and shared fixtures for CalTrans Bidding System tests

This file contains shared fixtures and configuration that can be used
across all test files in the test suite.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import json
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_pdf_path(test_data_dir):
    """Provide path to sample PDF file for testing"""
    pdf_path = test_data_dir / "sample_catalog.pdf"
    if not pdf_path.exists():
        # Create a dummy PDF file for testing
        pdf_path.parent.mkdir(exist_ok=True)
        with open(pdf_path, 'wb') as f:
            f.write(b"%PDF-1.4\n%Sample PDF content for testing")
    return pdf_path


@pytest.fixture(scope="session")
def sample_catalog_data():
    """Provide sample catalog data for testing"""
    return pd.DataFrame({
        'sku': ['WC001', 'WC002', 'WC003', 'WC004', 'WC005'],
        'product_name': ['2x4 Lumber', 'Plywood Sheathing', 'Concrete Form Tie', 'Form Spacer', 'Dimensional Lumber'],
        'description': ['Standard 2x4 Lumber', 'Plywood Sheathing', 'Concrete Form Tie', 'Concrete Form Spacer', 'Dimensional Lumber'],
        'size': ['2x4x8', '4x8x3/4', '1/2"x8"', '6"x6"', '2x6x12'],
        'unit': ['LF', 'SF', 'EA', 'EA', 'LF'],
        'price': [5.99, 12.50, 0.85, 1.25, 8.75],
        'category': ['lumber', 'lumber', 'formwork', 'formwork', 'lumber'],
        'construction_relevance': ['high', 'high', 'high', 'medium', 'high'],
        'confidence_score': [0.95, 0.90, 0.85, 0.80, 0.88]
    })


@pytest.fixture(scope="session")
def sample_analysis_data():
    """Provide sample analysis data for testing"""
    return {
        'terms': [
            {
                'term': 'BALUSTER',
                'category': 'safety',
                'priority': 'high',
                'context': 'BALUSTER installation for bridge railing',
                'confidence': 0.95,
                'page_number': 1
            },
            {
                'term': 'TYPE_86H_RAIL',
                'category': 'safety',
                'priority': 'high',
                'context': 'TYPE_86H_RAIL system for safety barriers',
                'confidence': 0.90,
                'page_number': 1
            },
            {
                'term': 'BLOCKOUT',
                'category': 'formwork',
                'priority': 'medium',
                'context': 'BLOCKOUT for utility penetrations',
                'confidence': 0.85,
                'page_number': 1
            }
        ],
        'quantities': [
            {
                'value': 2500.0,
                'unit': 'SQFT',
                'context': 'Bridge deck concrete',
                'page_number': 1,
                'confidence': 0.95
            },
            {
                'value': 1200.0,
                'unit': 'LF',
                'context': 'Formwork installation',
                'page_number': 1,
                'confidence': 0.90
            },
            {
                'value': 50.0,
                'unit': 'EA',
                'context': 'BALUSTER installation',
                'page_number': 1,
                'confidence': 0.85
            },
            {
                'value': 500.0,
                'unit': 'CY',
                'context': 'Concrete volume',
                'page_number': 1,
                'confidence': 0.88
            }
        ],
        'alerts': [
            {
                'title': 'High Priority Safety Item',
                'description': 'BALUSTER installation requires special attention',
                'severity': 'high',
                'recommendation': 'Ensure proper installation procedures are followed'
            }
        ],
        'warnings': [
            {
                'title': 'Formwork Requirements',
                'description': 'BLOCKOUT requirements need verification',
                'severity': 'medium',
                'recommendation': 'Review formwork specifications'
            }
        ],
        'summary': {
            'total_terms': 3,
            'total_quantities': 4,
            'findings': [
                'Safety items identified: BALUSTER, TYPE_86H_RAIL',
                'Formwork requirements: BLOCKOUT',
                'Concrete quantities: 2,500 SQFT deck, 500 CY volume'
            ],
            'processing_stats': {
                'pages_processed': 1,
                'processing_time': 2.5,
                'confidence_score': 0.89
            }
        }
    }


@pytest.fixture(scope="session")
def sample_bid_config():
    """Provide sample bid configuration for testing"""
    return {
        'project_name': 'Test Bridge Project',
        'project_number': '04-123456',
        'contract_type': 'Construction',
        'bid_date': datetime.now().date(),
        'completion_date': (datetime.now() + timedelta(days=365)).date(),
        'project_location': 'Los Angeles County',
        'project_description': 'Bridge deck replacement and safety improvements',
        'markup_percentage': 15.0,
        'overhead_rate': 10.0,
        'profit_margin': 8.0,
        'contingency_rate': 5.0,
        'tax_rate': 8.25,
        'currency': 'USD',
        'include_alternates': True,
        'use_escalation': False,
        'escalation_rate': 3.0,
        'bid_validity_days': 90
    }


@pytest.fixture(scope="session")
def sample_bid_items():
    """Provide sample bid items for testing"""
    return [
        {
            'item_number': '001',
            'description': 'Concrete, Class A, 3000 PSI',
            'quantity': 100.0,
            'unit': 'CY',
            'unit_price': 150.00,
            'total_price': 15000.00,
            'category': 'Materials',
            'notes': 'Standard concrete mix'
        },
        {
            'item_number': '002',
            'description': 'Reinforcing Steel, Grade 60',
            'quantity': 5000.0,
            'unit': 'LB',
            'unit_price': 0.85,
            'total_price': 4250.00,
            'category': 'Materials',
            'notes': 'Deformed bars'
        },
        {
            'item_number': '003',
            'description': 'Excavation, Common',
            'quantity': 200.0,
            'unit': 'CY',
            'unit_price': 25.00,
            'total_price': 5000.00,
            'category': 'Earthwork',
            'notes': 'Unclassified excavation'
        },
        {
            'item_number': '004',
            'description': 'Formwork Installation',
            'quantity': 500.0,
            'unit': 'SF',
            'unit_price': 12.50,
            'total_price': 6250.00,
            'category': 'Labor',
            'notes': 'Wood formwork'
        },
        {
            'item_number': '005',
            'description': 'BALUSTER Installation',
            'quantity': 50.0,
            'unit': 'EA',
            'unit_price': 45.00,
            'total_price': 2250.00,
            'category': 'Safety',
            'notes': 'Bridge railing installation'
        }
    ]


@pytest.fixture(scope="session")
def sample_pdf_content():
    """Provide sample PDF content for testing"""
    return """
    BRIDGE DECK CONCRETE SPECIFICATIONS
    
    Section 1: Concrete Requirements
    - Bridge deck concrete: 2,500 SQFT
    - Formwork installation: 1,200 LF
    - BALUSTER installation: 50 EA
    - Concrete volume: 500 CY
    - RETAINING_WALL construction: 800 SQFT
    
    Section 2: Formwork Details
    - TYPE_86H_RAIL system for safety barriers
    - BLOCKOUT for utility penetrations
    - STAMPED_CONCRETE finish for architectural treatment
    - FRACTURED_RIB_TEXTURE for wall surfaces
    
    Section 3: Materials
    - Concrete mix: 4,000 PSI
    - Rebar: Grade 60, 5,000 LB
    - Form ties: 1/2" diameter, 8" length
    - Spacers: 6" x 6" concrete blocks
    
    Section 4: Safety Requirements
    - BALUSTER installation per CalTrans standards
    - TYPE_86H_RAIL system for bridge safety
    - Proper formwork BLOCKOUT for utilities
    - Safety barriers and signage installation
    """


@pytest.fixture(scope="function")
def temp_file():
    """Provide a temporary file for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        yield tmp_file.name
    # Cleanup after test
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def temp_excel_file():
    """Provide a temporary Excel file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        yield tmp_file.name
    # Cleanup after test
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def temp_csv_file():
    """Provide a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
        yield tmp_file.name
    # Cleanup after test
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def mock_pdf_reader():
    """Provide a mock PDF reader for testing"""
    with patch('pdfplumber.open') as mock_open:
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF content"
        mock_page.extract_tables.return_value = []
        mock_pdf.pages = [mock_page] * 5
        mock_open.return_value.__enter__.return_value = mock_pdf
        yield mock_open


@pytest.fixture(scope="function")
def mock_excel_writer():
    """Provide a mock Excel writer for testing"""
    with patch('pandas.ExcelWriter') as mock_writer:
        mock_writer.return_value.__enter__.return_value = mock_writer.return_value
        yield mock_writer


@pytest.fixture(scope="session")
def performance_thresholds():
    """Provide performance thresholds for testing"""
    return {
        'max_processing_time_seconds': 10.0,
        'max_memory_increase_mb': 200,
        'min_confidence_score': 0.7,
        'max_error_rate': 0.05
    }


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        'test_mode': True,
        'verbose_output': False,
        'save_test_results': True,
        'test_data_dir': 'test_data',
        'output_dir': 'test_output'
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Mark tests with "performance" in name as performance tests
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        
        # Mark tests with "integration" in name as integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark tests with "slow" in name as slow tests
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark all other tests as unit tests
        if not any(marker in item.name.lower() for marker in ["performance", "integration", "slow"]):
            item.add_marker(pytest.mark.unit)


# Test utilities
def assert_dataframe_structure(df, expected_columns, min_rows=0):
    """Assert DataFrame has expected structure"""
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == len(expected_columns)
    for col in expected_columns:
        assert col in df.columns
    assert len(df) >= min_rows


def assert_pricing_calculations(pricing, expected_subtotal):
    """Assert pricing calculations are correct"""
    assert pricing['subtotal'] == pytest.approx(expected_subtotal, rel=1e-6)
    assert pricing['markup_amount'] >= 0
    assert pricing['overhead_amount'] >= 0
    assert pricing['profit_amount'] >= 0
    assert pricing['contingency_amount'] >= 0
    assert pricing['tax_amount'] >= 0
    assert pricing['grand_total'] >= pricing['subtotal']


def assert_file_exists_and_readable(file_path):
    """Assert file exists and is readable"""
    path = Path(file_path)
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.is_file()


def create_test_dataframe(data_dict):
    """Create a test DataFrame from dictionary"""
    return pd.DataFrame(data_dict)


def create_mock_bid_result(config, items, pricing):
    """Create a mock bid result for testing"""
    return Mock(
        config=config,
        items=items,
        subtotal=pricing['subtotal'],
        markup_amount=pricing['markup_amount'],
        overhead_amount=pricing['overhead_amount'],
        profit_amount=pricing['profit_amount'],
        contingency_amount=pricing['contingency_amount'],
        tax_amount=pricing['tax_amount'],
        grand_total=pricing['grand_total'],
        generated_at=datetime.now()
    ) 