"""
Unit tests for CalTransPDFAnalyzer

Comprehensive test suite covering:
- CalTrans terminology detection
- Quantity extraction accuracy
- Cross-reference functionality
- Alert generation
- Error handling
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

from src.analyzers.caltrans_analyzer import (
    CalTransPDFAnalyzer,
    CalTransTerm,
    Quantity,
    LumberRequirements,
    AnalysisResult,
    analyze_caltrans_pdf,
    extract_quantities_from_text,
    find_caltrans_terms
)


class TestCalTransPDFAnalyzer:
    """Test suite for CalTransPDFAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create a basic analyzer instance for testing"""
        return CalTransPDFAnalyzer()
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing"""
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
        """
    
    @pytest.fixture
    def sample_terms(self):
        """Sample CalTrans terms for testing"""
        return [
            CalTransTerm(
                term="BALUSTER",
                category="safety",
                priority="high",
                context="BALUSTER installation for bridge railing",
                confidence=0.95,
                page_number=1
            ),
            CalTransTerm(
                term="TYPE_86H_RAIL",
                category="safety",
                priority="high",
                context="TYPE_86H_RAIL system for safety barriers",
                confidence=0.90,
                page_number=1
            ),
            CalTransTerm(
                term="BLOCKOUT",
                category="formwork",
                priority="medium",
                context="BLOCKOUT for utility penetrations",
                confidence=0.85,
                page_number=1
            )
        ]
    
    @pytest.fixture
    def sample_quantities(self):
        """Sample quantities for testing"""
        return [
            Quantity(
                value=2500.0,
                unit="SQFT",
                context="Bridge deck concrete",
                page_number=1,
                confidence=0.95
            ),
            Quantity(
                value=1200.0,
                unit="LF",
                context="Formwork installation",
                page_number=1,
                confidence=0.90
            ),
            Quantity(
                value=50.0,
                unit="EA",
                context="BALUSTER installation",
                page_number=1,
                confidence=0.85
            ),
            Quantity(
                value=500.0,
                unit="CY",
                context="Concrete volume",
                page_number=1,
                confidence=0.88
            )
        ]

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert analyzer.terminology_patterns is not None
        assert analyzer.quantity_patterns is not None
        assert analyzer.cross_reference_data is not None

    def test_load_terminology_patterns(self, analyzer):
        """Test loading terminology patterns"""
        patterns = analyzer._load_terminology_patterns()
        assert isinstance(patterns, dict)
        assert "safety" in patterns
        assert "formwork" in patterns
        assert "concrete" in patterns
        
        # Test pattern matching
        test_text = "BALUSTER installation required"
        assert any(pattern.search(test_text) for pattern in patterns["safety"])

    def test_load_quantity_patterns(self, analyzer):
        """Test loading quantity patterns"""
        patterns = analyzer._load_quantity_patterns()
        assert isinstance(patterns, dict)
        assert "area" in patterns
        assert "volume" in patterns
        assert "length" in patterns
        assert "count" in patterns
        
        # Test pattern matching
        test_text = "Concrete: 2,500 SQFT"
        assert patterns["area"].search(test_text) is not None

    def test_load_cross_reference_data(self, analyzer):
        """Test loading cross-reference data"""
        data = analyzer._load_cross_reference_data()
        assert isinstance(data, dict)
        assert "terminology" in data
        assert "quantities" in data
        assert "specifications" in data

    def test_analyze_pdf(self, analyzer, sample_pdf_content):
        """Test PDF analysis functionality"""
        result = analyzer.analyze_pdf(sample_pdf_content)
        
        assert isinstance(result, AnalysisResult)
        assert result.terms is not None
        assert result.quantities is not None
        assert result.alerts is not None
        assert result.warnings is not None
        assert result.summary is not None

    def test_find_caltrans_terms(self, analyzer, sample_pdf_content):
        """Test CalTrans terminology detection"""
        terms = analyzer._find_caltrans_terms(sample_pdf_content, 1, [])
        
        assert isinstance(terms, list)
        assert len(terms) > 0
        
        # Check for specific terms
        term_texts = [term.term for term in terms]
        assert "BALUSTER" in term_texts
        assert "TYPE_86H_RAIL" in term_texts
        assert "BLOCKOUT" in term_texts
        
        # Check term properties
        for term in terms:
            assert term.term is not None
            assert term.category is not None
            assert term.priority is not None
            assert term.confidence > 0
            assert term.page_number == 1

    def test_extract_quantities(self, analyzer, sample_pdf_content):
        """Test quantity extraction from text"""
        quantities = analyzer._extract_quantities(sample_pdf_content, 1)
        
        assert isinstance(quantities, list)
        assert len(quantities) > 0
        
        # Check for specific quantities
        quantity_values = [(q.value, q.unit) for q in quantities]
        assert (2500.0, "SQFT") in quantity_values
        assert (1200.0, "LF") in quantity_values
        assert (50.0, "EA") in quantity_values
        assert (500.0, "CY") in quantity_values
        
        # Check quantity properties
        for quantity in quantities:
            assert quantity.value > 0
            assert quantity.unit is not None
            assert quantity.context is not None
            assert quantity.confidence > 0
            assert quantity.page_number == 1

    def test_extract_quantities_with_various_formats(self, analyzer):
        """Test quantity extraction with various formats"""
        test_text = """
        Concrete: 2,500 SQFT
        Lumber: 1,200 LF
        Bolts: 50 EA
        Volume: 500 CY
        Weight: 5,000 LB
        Time: 30 DAYS
        """
        
        quantities = analyzer._extract_quantities(test_text, 1)
        
        assert len(quantities) >= 6
        
        # Check different units
        units = [q.unit for q in quantities]
        assert "SQFT" in units
        assert "LF" in units
        assert "EA" in units
        assert "CY" in units
        assert "LB" in units
        assert "DAYS" in units

    def test_extract_quantities_with_decimal_values(self, analyzer):
        """Test quantity extraction with decimal values"""
        test_text = """
        Concrete: 2,500.5 SQFT
        Lumber: 1,200.75 LF
        Bolts: 50.0 EA
        """
        
        quantities = analyzer._extract_quantities(test_text, 1)
        
        assert len(quantities) >= 3
        
        # Check decimal values
        for quantity in quantities:
            assert isinstance(quantity.value, float)
            assert quantity.value > 0

    def test_cross_reference_terminology(self, analyzer, sample_terms):
        """Test terminology cross-referencing"""
        cross_refs = analyzer._cross_reference_terminology(sample_terms)
        
        assert isinstance(cross_refs, list)
        assert len(cross_refs) > 0
        
        # Check cross-reference properties
        for cross_ref in cross_refs:
            assert cross_ref.term is not None
            assert cross_ref.related_terms is not None
            assert cross_ref.specifications is not None
            assert cross_ref.requirements is not None

    def test_cross_reference_quantities(self, analyzer, sample_quantities):
        """Test quantity cross-referencing"""
        cross_refs = analyzer._cross_reference_quantities(sample_quantities)
        
        assert isinstance(cross_refs, list)
        assert len(cross_refs) > 0
        
        # Check cross-reference properties
        for cross_ref in cross_refs:
            assert cross_ref.quantity is not None
            assert cross_ref.related_quantities is not None
            assert cross_ref.specifications is not None
            assert cross_ref.requirements is not None

    def test_generate_alerts(self, analyzer, sample_terms, sample_quantities):
        """Test alert generation"""
        alerts = analyzer._generate_alerts(sample_terms, sample_quantities)
        
        assert isinstance(alerts, list)
        
        # Check alert properties
        for alert in alerts:
            assert alert.title is not None
            assert alert.description is not None
            assert alert.severity in ["critical", "high", "medium", "low"]
            assert alert.recommendation is not None

    def test_generate_warnings(self, analyzer, sample_terms, sample_quantities):
        """Test warning generation"""
        warnings = analyzer._generate_warnings(sample_terms, sample_quantities)
        
        assert isinstance(warnings, list)
        
        # Check warning properties
        for warning in warnings:
            assert warning.title is not None
            assert warning.description is not None
            assert warning.severity in ["high", "medium", "low"]
            assert warning.recommendation is not None

    def test_calculate_lumber_requirements(self, analyzer, sample_terms, sample_quantities):
        """Test lumber requirement calculations"""
        lumber_req = analyzer.calculate_lumber_requirements(sample_terms, sample_quantities)
        
        assert isinstance(lumber_req, LumberRequirements)
        assert lumber_req.total_board_feet >= 0
        assert lumber_req.plywood_sheets >= 0
        assert lumber_req.formwork_area >= 0
        assert lumber_req.estimated_cost >= 0

    def test_calculate_lumber_requirements_with_formwork(self, analyzer):
        """Test lumber calculations with formwork terms"""
        formwork_terms = [
            CalTransTerm(
                term="FORM_FACING",
                category="formwork",
                priority="high",
                context="FORM_FACING installation",
                confidence=0.95,
                page_number=1
            )
        ]
        
        formwork_quantities = [
            Quantity(
                value=5000.0,
                unit="SQFT",
                context="Formwork area",
                page_number=1,
                confidence=0.90
            )
        ]
        
        lumber_req = analyzer.calculate_lumber_requirements(formwork_terms, formwork_quantities)
        
        assert lumber_req.formwork_area == 5000.0
        assert lumber_req.plywood_sheets > 0
        assert lumber_req.total_board_feet > 0

    def test_validate_quantities(self, analyzer, sample_quantities):
        """Test quantity validation"""
        validation_results = analyzer._validate_quantities(sample_quantities)
        
        assert isinstance(validation_results, list)
        
        for result in validation_results:
            assert result.quantity is not None
            assert result.is_valid is not None
            assert result.issues is not None
            assert result.recommendations is not None

    def test_validate_terminology(self, analyzer, sample_terms):
        """Test terminology validation"""
        validation_results = analyzer._validate_terminology(sample_terms)
        
        assert isinstance(validation_results, list)
        
        for result in validation_results:
            assert result.term is not None
            assert result.is_valid is not None
            assert result.issues is not None
            assert result.recommendations is not None

    def test_generate_summary(self, analyzer, sample_terms, sample_quantities):
        """Test summary generation"""
        summary = analyzer._generate_summary(sample_terms, sample_quantities)
        
        assert isinstance(summary, dict)
        assert "total_terms" in summary
        assert "total_quantities" in summary
        assert "findings" in summary
        assert "processing_stats" in summary
        
        assert summary["total_terms"] == len(sample_terms)
        assert summary["total_quantities"] == len(sample_quantities)

    def test_error_handling_invalid_pdf(self, analyzer):
        """Test error handling for invalid PDF content"""
        with pytest.raises(Exception):
            analyzer.analyze_pdf("")

    def test_error_handling_none_content(self, analyzer):
        """Test error handling for None content"""
        with pytest.raises(Exception):
            analyzer.analyze_pdf(None)

    def test_confidence_score_calculation(self, analyzer):
        """Test confidence score calculation"""
        # Test high confidence
        high_conf_term = analyzer._find_caltrans_terms("BALUSTER installation", 1, [])
        if high_conf_term:
            assert high_conf_term[0].confidence >= 0.8
        
        # Test medium confidence
        med_conf_term = analyzer._find_caltrans_terms("formwork installation", 1, [])
        if med_conf_term:
            assert 0.5 <= med_conf_term[0].confidence <= 0.8
        
        # Test low confidence
        low_conf_term = analyzer._find_caltrans_terms("random text", 1, [])
        if low_conf_term:
            assert low_conf_term[0].confidence <= 0.5

    def test_priority_assignment(self, analyzer):
        """Test priority assignment for terms"""
        safety_terms = analyzer._find_caltrans_terms("BALUSTER TYPE_86H_RAIL", 1, [])
        
        for term in safety_terms:
            if term.term in ["BALUSTER", "TYPE_86H_RAIL"]:
                assert term.priority == "high"

    def test_category_assignment(self, analyzer):
        """Test category assignment for terms"""
        formwork_terms = analyzer._find_caltrans_terms("BLOCKOUT FORM_FACING", 1, [])
        
        for term in formwork_terms:
            if term.term in ["BLOCKOUT", "FORM_FACING"]:
                assert term.category == "formwork"

    def test_quantity_unit_detection(self, analyzer):
        """Test quantity unit detection"""
        test_text = """
        Area: 2,500 SQFT
        Length: 1,200 LF
        Volume: 500 CY
        Count: 50 EA
        Weight: 5,000 LB
        """
        
        quantities = analyzer._extract_quantities(test_text, 1)
        
        units = [q.unit for q in quantities]
        assert "SQFT" in units
        assert "LF" in units
        assert "CY" in units
        assert "EA" in units
        assert "LB" in units

    def test_context_extraction(self, analyzer):
        """Test context extraction for terms and quantities"""
        test_text = "Bridge deck concrete: 2,500 SQFT for main span"
        
        quantities = analyzer._extract_quantities(test_text, 1)
        terms = analyzer._find_caltrans_terms(test_text, 1, [])
        
        if quantities:
            assert "Bridge deck concrete" in quantities[0].context
        
        if terms:
            assert "Bridge deck concrete" in terms[0].context


class TestAnalyzerFunctions:
    """Test suite for analyzer utility functions"""
    
    def test_analyze_caltrans_pdf_function(self, sample_pdf_content):
        """Test analyze_caltrans_pdf function"""
        result = analyze_caltrans_pdf(sample_pdf_content)
        
        assert isinstance(result, AnalysisResult)
        assert result.terms is not None
        assert result.quantities is not None

    def test_extract_quantities_from_text_function(self, sample_pdf_content):
        """Test extract_quantities_from_text function"""
        quantities = extract_quantities_from_text(sample_pdf_content)
        
        assert isinstance(quantities, list)
        assert len(quantities) > 0
        
        for quantity in quantities:
            assert quantity.value > 0
            assert quantity.unit is not None

    def test_find_caltrans_terms_function(self, sample_pdf_content):
        """Test find_caltrans_terms function"""
        terms = find_caltrans_terms(sample_pdf_content)
        
        assert isinstance(terms, list)
        assert len(terms) > 0
        
        for term in terms:
            assert term.term is not None
            assert term.category is not None


class TestAnalyzerPerformance:
    """Test suite for analyzer performance"""
    
    def test_large_text_processing(self):
        """Test processing of large text content"""
        analyzer = CalTransPDFAnalyzer()
        
        # Create large text content
        large_text = "Bridge deck concrete: 2,500 SQFT. " * 1000
        large_text += "BALUSTER installation: 50 EA. " * 1000
        
        # Test processing time
        import time
        start_time = time.time()
        result = analyzer.analyze_pdf(large_text)
        processing_time = time.time() - start_time
        
        assert processing_time < 10.0  # Should process in under 10 seconds
        assert result.terms is not None
        assert result.quantities is not None

    def test_memory_usage_large_content(self):
        """Test memory usage with large content"""
        analyzer = CalTransPDFAnalyzer()
        
        # Create memory-intensive content
        large_text = "Sample content " * 10000
        
        # Test memory efficiency
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large content
        result = analyzer.analyze_pdf(large_text)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        assert memory_increase < 200  # Should not increase memory by more than 200MB


class TestAnalyzerEdgeCases:
    """Test suite for analyzer edge cases"""
    
    def test_empty_text_processing(self):
        """Test processing of empty text"""
        analyzer = CalTransPDFAnalyzer()
        
        result = analyzer.analyze_pdf("")
        
        assert isinstance(result, AnalysisResult)
        assert len(result.terms) == 0
        assert len(result.quantities) == 0

    def test_special_characters_handling(self):
        """Test handling of special characters"""
        analyzer = CalTransPDFAnalyzer()
        
        special_text = """
        Concrete: 2,500 SQFT (with special chars: @#$%^&*)
        BALUSTER installation: 50 EA [brackets] {braces}
        """
        
        result = analyzer.analyze_pdf(special_text)
        
        assert isinstance(result, AnalysisResult)
        assert len(result.quantities) > 0
        assert len(result.terms) > 0

    def test_mixed_case_handling(self):
        """Test handling of mixed case text"""
        analyzer = CalTransPDFAnalyzer()
        
        mixed_case_text = """
        Concrete: 2,500 SQFT
        baluster installation: 50 EA
        TYPE_86H_RAIL system
        """
        
        result = analyzer.analyze_pdf(mixed_case_text)
        
        assert isinstance(result, AnalysisResult)
        assert len(result.quantities) > 0
        assert len(result.terms) > 0

    def test_duplicate_terms_handling(self):
        """Test handling of duplicate terms"""
        analyzer = CalTransPDFAnalyzer()
        
        duplicate_text = """
        BALUSTER installation: 50 EA
        BALUSTER installation: 50 EA
        BALUSTER installation: 50 EA
        """
        
        result = analyzer.analyze_pdf(duplicate_text)
        
        assert isinstance(result, AnalysisResult)
        # Should handle duplicates appropriately
        assert len(result.terms) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 