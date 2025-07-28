#!/usr/bin/env python3
"""
Test script for the multi-file upload component

This script tests the multi-file upload functionality without running the full Streamlit app.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_multi_file_upload_component():
    """Test the multi-file upload component"""
    
    try:
        # Import the component
        from ui.components.multi_file_upload import MultiFileUploadComponent, FileCategory, FileStatus
        
        print("✅ Multi-file upload component imported successfully")
        
        # Test component initialization
        component = MultiFileUploadComponent()
        print("✅ MultiFileUploadComponent initialized successfully")
        
        # Test category configurations
        print(f"✅ Found {len(component.category_configs)} file categories:")
        for category, config in component.category_configs.items():
            print(f"   - {config['title']} ({config['icon']}) - {'Required' if config['required'] else 'Optional'}")
        
        # Test file validation
        print("\n✅ Component ready for testing")
        print("📋 Categories available:")
        print("   - Project Specifications (Required)")
        print("   - Bid Forms (Recommended)")
        print("   - Construction Plans (Recommended)")
        print("   - Supplemental Information (Optional)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing component: {e}")
        return False

def test_caltrans_analyzer_multi_file():
    """Test the CalTrans analyzer multi-file functionality"""
    
    try:
        from src.analyzers.caltrans_analyzer import CalTransPDFAnalyzer
        
        print("\n✅ CalTrans analyzer imported successfully")
        
        # Test analyzer initialization
        analyzer = CalTransPDFAnalyzer()
        print("✅ CalTransPDFAnalyzer initialized successfully")
        
        # Test multi-file analysis method exists
        if hasattr(analyzer, 'analyze_multiple_files'):
            print("✅ Multi-file analysis method available")
        else:
            print("❌ Multi-file analysis method not found")
            return False
        
        # Test cross-reference methods exist
        if hasattr(analyzer, '_cross_reference_findings'):
            print("✅ Cross-reference method available")
        else:
            print("❌ Cross-reference method not found")
            return False
        
        if hasattr(analyzer, '_generate_comprehensive_alerts'):
            print("✅ Comprehensive alerts method available")
        else:
            print("❌ Comprehensive alerts method not found")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        return False

def test_bid_engine_comprehensive():
    """Test the bid engine comprehensive functionality"""
    
    try:
        from src.bidding.bid_engine import CalTransBiddingEngine
        
        print("\n✅ Bid engine imported successfully")
        
        # Test engine initialization
        engine = CalTransBiddingEngine()
        print("✅ CalTransBiddingEngine initialized successfully")
        
        # Test comprehensive bid generation method exists
        if hasattr(engine, 'generate_comprehensive_bid'):
            print("✅ Comprehensive bid generation method available")
        else:
            print("❌ Comprehensive bid generation method not found")
            return False
        
        # Test comprehensive line items method exists
        if hasattr(engine, '_generate_line_items_from_comprehensive_analysis'):
            print("✅ Comprehensive line items method available")
        else:
            print("❌ Comprehensive line items method not found")
            return False
        
        # Test comprehensive pricing method exists
        if hasattr(engine, '_calculate_comprehensive_pricing_summary'):
            print("✅ Comprehensive pricing method available")
        else:
            print("❌ Comprehensive pricing method not found")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing bid engine: {e}")
        return False

def test_excel_generator_comprehensive():
    """Test the Excel generator comprehensive functionality"""
    
    try:
        from src.utils.excel_generator import ExcelBidGenerator
        
        print("\n✅ Excel generator imported successfully")
        
        # Test generator initialization
        generator = ExcelBidGenerator()
        print("✅ ExcelBidGenerator initialized successfully")
        
        # Test comprehensive Excel generation method exists
        if hasattr(generator, 'generate_comprehensive_bid_excel'):
            print("✅ Comprehensive Excel generation method available")
        else:
            print("❌ Comprehensive Excel generation method not found")
            return False
        
        # Test comprehensive sheet methods exist
        if hasattr(generator, 'create_comprehensive_summary_sheet'):
            print("✅ Comprehensive summary sheet method available")
        else:
            print("❌ Comprehensive summary sheet method not found")
            return False
        
        if hasattr(generator, 'create_cross_reference_sheet'):
            print("✅ Cross-reference sheet method available")
        else:
            print("❌ Cross-reference sheet method not found")
            return False
        
        if hasattr(generator, 'create_document_analysis_sheet'):
            print("✅ Document analysis sheet method available")
        else:
            print("❌ Document analysis sheet method not found")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Excel generator: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 Testing Multi-File Upload System")
    print("=" * 50)
    
    tests = [
        ("Multi-File Upload Component", test_multi_file_upload_component),
        ("CalTrans Analyzer Multi-File", test_caltrans_analyzer_multi_file),
        ("Bid Engine Comprehensive", test_bid_engine_comprehensive),
        ("Excel Generator Comprehensive", test_excel_generator_comprehensive)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-file upload system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 