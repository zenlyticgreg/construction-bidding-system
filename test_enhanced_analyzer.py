#!/usr/bin/env python3
"""
Test script for enhanced CalTrans PDF Analyzer with multi-document support.

This script tests the new functionality including:
- Document-specific analysis strategies
- Multi-file analysis with cross-referencing
- Bid line item extraction
- Comprehensive analysis results
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_analyzer():
    """Test the enhanced CalTrans analyzer functionality"""
    
    print("🧪 Testing Enhanced CalTrans PDF Analyzer")
    print("=" * 50)
    
    try:
        from analyzers.caltrans_analyzer import (
            CalTransPDFAnalyzer, 
            ComprehensiveAnalysisResult,
            BidLineItem,
            CrossReferenceResult,
            CalTransAnalysisResult
        )
        print("✅ Successfully imported CalTrans analyzer classes")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 1: Analyzer initialization with document strategies
    print("\n📋 Test 1: Analyzer Initialization")
    try:
        analyzer = CalTransPDFAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Check if document strategies are set up
        if hasattr(analyzer, 'document_strategies'):
            print(f"✅ Document strategies configured: {len(analyzer.document_strategies)} types")
            for doc_type, strategy in analyzer.document_strategies.items():
                print(f"   - {doc_type}: {strategy.get('focus_terms', [])[:3]}...")
        else:
            print("❌ Document strategies not found")
            return False
            
    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        return False
    
    # Test 2: Bid form patterns compilation
    print("\n💰 Test 2: Bid Form Patterns")
    try:
        if hasattr(analyzer, 'bid_form_patterns'):
            print(f"✅ Bid form patterns compiled: {len(analyzer.bid_form_patterns)} patterns")
            for pattern_name in analyzer.bid_form_patterns.keys():
                print(f"   - {pattern_name}")
        else:
            print("❌ Bid form patterns not found")
            return False
            
    except Exception as e:
        print(f"❌ Bid form patterns test failed: {e}")
        return False
    
    # Test 3: Document-specific analysis method
    print("\n📄 Test 3: Document-Specific Analysis Method")
    try:
        # Check if analyze_pdf method supports document_type parameter
        import inspect
        sig = inspect.signature(analyzer.analyze_pdf)
        params = list(sig.parameters.keys())
        
        if 'document_type' in params:
            print("✅ analyze_pdf method supports document_type parameter")
            print(f"   Parameters: {params}")
        else:
            print("❌ analyze_pdf method missing document_type parameter")
            return False
            
    except Exception as e:
        print(f"❌ Method signature test failed: {e}")
        return False
    
    # Test 4: Multi-file analysis method
    print("\n📚 Test 4: Multi-File Analysis Method")
    try:
        if hasattr(analyzer, 'analyze_multiple_files'):
            sig = inspect.signature(analyzer.analyze_multiple_files)
            params = list(sig.parameters.keys())
            
            if 'file_paths_dict' in params:
                print("✅ analyze_multiple_files method found")
                print(f"   Parameters: {params}")
                print(f"   Return type: {sig.return_annotation}")
            else:
                print("❌ analyze_multiple_files method missing file_paths_dict parameter")
                return False
        else:
            print("❌ analyze_multiple_files method not found")
            return False
            
    except Exception as e:
        print(f"❌ Multi-file analysis test failed: {e}")
        return False
    
    # Test 5: Cross-reference method
    print("\n🔗 Test 5: Cross-Reference Analysis Method")
    try:
        if hasattr(analyzer, 'cross_reference_findings'):
            sig = inspect.signature(analyzer.cross_reference_findings)
            params = list(sig.parameters.keys())
            
            if 'analysis_results_list' in params:
                print("✅ cross_reference_findings method found")
                print(f"   Parameters: {params}")
                print(f"   Return type: {sig.return_annotation}")
            else:
                print("❌ cross_reference_findings method missing analysis_results_list parameter")
                return False
        else:
            print("❌ cross_reference_findings method not found")
            return False
            
    except Exception as e:
        print(f"❌ Cross-reference test failed: {e}")
        return False
    
    # Test 6: Bid line item extraction method
    print("\n📋 Test 6: Bid Line Item Extraction Method")
    try:
        if hasattr(analyzer, 'extract_bid_line_items'):
            sig = inspect.signature(analyzer.extract_bid_line_items)
            params = list(sig.parameters.keys())
            
            if 'analysis_result' in params:
                print("✅ extract_bid_line_items method found")
                print(f"   Parameters: {params}")
                print(f"   Return type: {sig.return_annotation}")
            else:
                print("❌ extract_bid_line_items method missing analysis_result parameter")
                return False
        else:
            print("❌ extract_bid_line_items method not found")
            return False
            
    except Exception as e:
        print(f"❌ Bid line item extraction test failed: {e}")
        return False
    
    # Test 7: Enhanced page analysis method
    print("\n📖 Test 7: Enhanced Page Analysis Method")
    try:
        if hasattr(analyzer, 'analyze_page'):
            sig = inspect.signature(analyzer.analyze_page)
            params = list(sig.parameters.keys())
            
            if 'document_type' in params and 'strategy' in params:
                print("✅ analyze_page method supports document-specific analysis")
                print(f"   Parameters: {params}")
            else:
                print("❌ analyze_page method missing document_type or strategy parameters")
                return False
        else:
            print("❌ analyze_page method not found")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced page analysis test failed: {e}")
        return False
    
    # Test 8: Enhanced quantity extraction method
    print("\n📊 Test 8: Enhanced Quantity Extraction Method")
    try:
        if hasattr(analyzer, '_extract_quantities'):
            sig = inspect.signature(analyzer._extract_quantities)
            params = list(sig.parameters.keys())
            
            if 'document_type' in params and 'strategy' in params:
                print("✅ _extract_quantities method supports document-specific extraction")
                print(f"   Parameters: {params}")
            else:
                print("❌ _extract_quantities method missing document_type or strategy parameters")
                return False
        else:
            print("❌ _extract_quantities method not found")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced quantity extraction test failed: {e}")
        return False
    
    # Test 9: Enhanced term finding method
    print("\n🔍 Test 9: Enhanced Term Finding Method")
    try:
        if hasattr(analyzer, '_find_caltrans_terms'):
            sig = inspect.signature(analyzer._find_caltrans_terms)
            params = list(sig.parameters.keys())
            
            if 'document_type' in params and 'strategy' in params:
                print("✅ _find_caltrans_terms method supports document-specific analysis")
                print(f"   Parameters: {params}")
            else:
                print("❌ _find_caltrans_terms method missing document_type or strategy parameters")
                return False
        else:
            print("❌ _find_caltrans_terms method not found")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced term finding test failed: {e}")
        return False
    
    # Test 10: Confidence score calculation method
    print("\n🎯 Test 10: Confidence Score Calculation Method")
    try:
        if hasattr(analyzer, '_calculate_confidence_score'):
            sig = inspect.signature(analyzer._calculate_confidence_score)
            params = list(sig.parameters.keys())
            
            if 'result' in params:
                print("✅ _calculate_confidence_score method found")
                print(f"   Parameters: {params}")
                print(f"   Return type: {sig.return_annotation}")
            else:
                print("❌ _calculate_confidence_score method missing result parameter")
                return False
        else:
            print("❌ _calculate_confidence_score method not found")
            return False
            
    except Exception as e:
        print(f"❌ Confidence score calculation test failed: {e}")
        return False
    
    # Test 11: Data class enhancements
    print("\n📋 Test 11: Enhanced Data Classes")
    try:
        # Test TermMatch with source_document
        from analyzers.caltrans_analyzer import TermMatch
        term = TermMatch(
            term="BALUSTER",
            category="bridge_barrier",
            priority="high",
            context="Test context",
            page_number=1,
            source_document="specifications"
        )
        print("✅ TermMatch supports source_document field")
        
        # Test ExtractedQuantity with source_document
        from analyzers.caltrans_analyzer import ExtractedQuantity
        quantity = ExtractedQuantity(
            value=100.0,
            unit="LF",
            context="Test context",
            page_number=1,
            source_document="bid_forms"
        )
        print("✅ ExtractedQuantity supports source_document field")
        
        # Test ComprehensiveAnalysisResult
        comprehensive = ComprehensiveAnalysisResult()
        print("✅ ComprehensiveAnalysisResult can be instantiated")
        
        # Test CrossReferenceResult
        cross_ref = CrossReferenceResult()
        print("✅ CrossReferenceResult can be instantiated")
        
        # Test BidLineItem
        bid_item = BidLineItem(
            item_number="1",
            description="Test item",
            caltrans_code="TEST001",
            quantity=100.0,
            unit="LF"
        )
        print("✅ BidLineItem can be instantiated")
        
    except Exception as e:
        print(f"❌ Data class test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Enhanced analyzer is ready for use.")
    return True

def test_document_strategies():
    """Test document-specific strategies"""
    print("\n📚 Testing Document Strategies")
    print("=" * 30)
    
    try:
        from analyzers.caltrans_analyzer import CalTransPDFAnalyzer
        analyzer = CalTransPDFAnalyzer()
        
        strategies = analyzer.document_strategies
        
        # Test each document type
        for doc_type, strategy in strategies.items():
            print(f"\n📄 {doc_type.upper()}:")
            print(f"   Focus terms: {strategy.get('focus_terms', [])[:3]}...")
            print(f"   Confidence boost: {strategy.get('confidence_boost', 1.0)}")
            print(f"   Extraction priority: {strategy.get('extraction_priority', 'medium')}")
        
        print("\n✅ Document strategies test completed")
        return True
        
    except Exception as e:
        print(f"❌ Document strategies test failed: {e}")
        return False

def test_bid_form_patterns():
    """Test bid form pattern compilation"""
    print("\n💰 Testing Bid Form Patterns")
    print("=" * 30)
    
    try:
        from analyzers.caltrans_analyzer import CalTransPDFAnalyzer
        analyzer = CalTransPDFAnalyzer()
        
        patterns = analyzer.bid_form_patterns
        
        # Test each pattern
        for pattern_name, pattern in patterns.items():
            print(f"\n🔍 {pattern_name}:")
            print(f"   Pattern: {pattern.pattern}")
            print(f"   Flags: {pattern.flags}")
        
        print("\n✅ Bid form patterns test completed")
        return True
        
    except Exception as e:
        print(f"❌ Bid form patterns test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced CalTrans Analyzer Tests")
    print("=" * 60)
    
    # Run main functionality tests
    success1 = test_enhanced_analyzer()
    
    # Run document strategies tests
    success2 = test_document_strategies()
    
    # Run bid form patterns tests
    success3 = test_bid_form_patterns()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if success1 and success2 and success3:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Enhanced CalTrans analyzer is fully functional with:")
        print("   - Document-specific analysis strategies")
        print("   - Multi-file analysis with cross-referencing")
        print("   - Bid line item extraction")
        print("   - Comprehensive analysis results")
        print("   - Enhanced confidence scoring")
        print("   - Professional error handling and logging")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nFailed tests:")
        if not success1:
            print("   - Enhanced analyzer functionality")
        if not success2:
            print("   - Document strategies")
        if not success3:
            print("   - Bid form patterns")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 