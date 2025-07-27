# CalTrans Bidding System - Test Suite

This directory contains comprehensive unit tests for the CalTrans Bidding System, covering all major components and functionality.

## 📋 Test Structure

### Test Files

- **`test_extractor.py`** - Tests for `WhitecapCatalogExtractor`
  - PDF processing capabilities
  - Product categorization
  - Data validation
  - Error handling
  - Performance metrics

- **`test_analyzer.py`** - Tests for `CalTransPDFAnalyzer`
  - CalTrans terminology detection
  - Quantity extraction accuracy
  - Cross-reference functionality
  - Alert generation
  - Edge cases and error handling

- **`test_bidding.py`** - Tests for bidding system
  - Bid generation workflow
  - Pricing calculations
  - Product matching accuracy
  - Excel output validation
  - Performance testing

- **`conftest.py`** - Shared fixtures and configuration
  - Common test data
  - Mock objects
  - Utility functions
  - Pytest configuration

### Test Categories

Tests are categorized using pytest markers:

- **`@pytest.mark.unit`** - Unit tests (fast, isolated)
- **`@pytest.mark.integration`** - Integration tests (component interaction)
- **`@pytest.mark.performance`** - Performance tests (timing, memory)
- **`@pytest.mark.slow`** - Slow tests (long-running operations)

## 🚀 Quick Start

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Install pytest and testing tools:
```bash
pip install pytest pytest-cov pytest-xdist pytest-mock
```

### Running Tests

#### Using the Test Runner (Recommended)

```bash
# Run all tests
python run_tests.py --all

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Run specific components
python run_tests.py --extractor
python run_tests.py --analyzer
python run_tests.py --bidding

# Run with coverage
python run_tests.py --coverage

# Run in parallel
python run_tests.py --parallel

# Check test environment
python run_tests.py --check-env
```

#### Using pytest directly

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_extractor.py -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests in parallel
pytest tests/ -n auto

# Run specific test markers
pytest tests/ -m unit
pytest tests/ -m "not slow"
```

## 📊 Test Coverage

### Extractor Tests (`test_extractor.py`)

**Core Functionality:**
- ✅ PDF processing and text extraction
- ✅ Table data extraction and parsing
- ✅ Product data structure validation
- ✅ Category assignment and classification
- ✅ Confidence score calculation
- ✅ Data cleaning and validation

**Error Handling:**
- ✅ Invalid PDF files
- ✅ Corrupted data
- ✅ Missing required fields
- ✅ Empty or malformed content

**Performance:**
- ✅ Large dataset processing
- ✅ Memory usage optimization
- ✅ Processing time benchmarks

### Analyzer Tests (`test_analyzer.py`)

**Core Functionality:**
- ✅ CalTrans terminology detection
- ✅ Quantity extraction with various formats
- ✅ Cross-reference analysis
- ✅ Alert and warning generation
- ✅ Lumber requirement calculations

**Accuracy Testing:**
- ✅ Pattern matching precision
- ✅ Unit detection accuracy
- ✅ Context extraction quality
- ✅ Confidence score validation

**Edge Cases:**
- ✅ Special characters handling
- ✅ Mixed case text processing
- ✅ Duplicate term handling
- ✅ Empty content processing

### Bidding Tests (`test_bidding.py`)

**Core Functionality:**
- ✅ Bid generation workflow
- ✅ Pricing calculations (markup, overhead, profit, tax)
- ✅ Product matching to catalog
- ✅ Excel output generation
- ✅ Bid validation and quality checks

**Calculation Accuracy:**
- ✅ Subtotal calculations
- ✅ Percentage-based adjustments
- ✅ Tax calculations
- ✅ Grand total validation

**Excel Generation:**
- ✅ File creation and formatting
- ✅ Multiple sheet generation
- ✅ Data validation in Excel
- ✅ Professional formatting

## 🧪 Test Fixtures

### Shared Fixtures (`conftest.py`)

```python
# Sample data fixtures
sample_catalog_data()      # Catalog DataFrame
sample_analysis_data()     # Analysis results
sample_bid_config()        # Bid configuration
sample_bid_items()         # Bid line items
sample_pdf_content()       # PDF text content

# File fixtures
temp_file()               # Temporary file
temp_excel_file()         # Temporary Excel file
temp_csv_file()           # Temporary CSV file

# Mock fixtures
mock_pdf_reader()         # Mock PDF reader
mock_excel_writer()       # Mock Excel writer

# Configuration fixtures
performance_thresholds()  # Performance limits
test_config()            # Test configuration
```

### Usage Example

```python
def test_extractor_with_sample_data(extractor, sample_catalog_data):
    """Test extractor with sample catalog data"""
    result = extractor.process_catalog(sample_catalog_data)
    assert len(result) > 0
    assert result['confidence_score'] > 0.7
```

## 📈 Performance Testing

### Performance Thresholds

Tests include performance benchmarks to ensure the system meets requirements:

- **Processing Time**: < 10 seconds for large datasets
- **Memory Usage**: < 200MB increase for large operations
- **Confidence Score**: > 70% minimum accuracy
- **Error Rate**: < 5% maximum error rate

### Running Performance Tests

```bash
# Run only performance tests
python run_tests.py --performance

# Run with performance monitoring
pytest tests/ -m performance --durations=10
```

## 🔧 Test Configuration

### Pytest Configuration

The test suite uses custom pytest configuration in `conftest.py`:

- **Custom markers** for test categorization
- **Shared fixtures** for common test data
- **Performance thresholds** for benchmarking
- **Utility functions** for common assertions

### Environment Variables

```bash
# Set test environment
export TEST_MODE=true
export VERBOSE_OUTPUT=false
export SAVE_TEST_RESULTS=true
```

## 📝 Writing New Tests

### Test Structure

```python
class TestNewComponent:
    """Test suite for new component"""
    
    @pytest.fixture
    def component(self):
        """Create component instance for testing"""
        return NewComponent()
    
    def test_basic_functionality(self, component):
        """Test basic functionality"""
        result = component.process_data("test input")
        assert result is not None
        assert result.success is True
    
    def test_error_handling(self, component):
        """Test error handling"""
        with pytest.raises(ValueError):
            component.process_data("")
    
    @pytest.mark.performance
    def test_performance(self, component):
        """Test performance with large dataset"""
        large_data = "x" * 1000000
        start_time = time.time()
        result = component.process_data(large_data)
        processing_time = time.time() - start_time
        
        assert processing_time < 5.0  # Should complete in under 5 seconds
```

### Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures** for common setup and teardown
4. **Test edge cases** and error conditions
5. **Include performance tests** for critical operations
6. **Use appropriate markers** to categorize tests
7. **Write comprehensive assertions** to validate results

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**: Ensure `src` directory is in Python path
2. **Missing Dependencies**: Install all required packages
3. **File Path Issues**: Use `Path` objects for cross-platform compatibility
4. **Mock Configuration**: Verify mock objects are properly configured

### Debug Commands

```bash
# Run with detailed output
pytest tests/ -v -s

# Run single test with debugging
pytest tests/test_extractor.py::TestWhitecapCatalogExtractor::test_extractor_initialization -v -s

# Run with print statements
pytest tests/ -s

# Run with coverage and show missing lines
pytest tests/ --cov=src --cov-report=term-missing
```

## 📊 Test Reports

### Coverage Reports

```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View coverage report
open htmlcov/index.html
```

### Test Results

```bash
# Generate JUnit XML report
pytest tests/ --junitxml=test-results.xml

# Generate test report with all formats
python run_tests.py --report
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist
      - name: Run tests
        run: python run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Include both positive and negative test cases
3. Add appropriate markers for test categorization
4. Update this README if adding new test categories
5. Ensure all tests pass before submitting

For questions or issues with the test suite, please refer to the main project documentation or create an issue in the repository. 