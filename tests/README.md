# PACE - Project Analysis & Construction Estimating - Test Suite

This directory contains comprehensive unit tests for the PACE construction bidding automation platform, covering all major components and functionality.

## 📁 Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_analyzer.py         # Analyzer component tests
├── test_bid_engine.py       # Bid engine tests
├── test_bidding.py          # Bidding system tests
├── test_caltrans_analyzer.py # CalTrans-specific analyzer tests
├── test_extractor.py        # Extractor component tests
├── test_product_matcher.py  # Product matcher tests
├── test_ui_components.py    # UI component tests
└── README.md               # This file
```

## 🧪 Test Categories

### Unit Tests
- **Component Tests**: Individual component functionality
- **Utility Tests**: Helper function and utility testing
- **Data Structure Tests**: Data model and validation testing

### Integration Tests
- **Workflow Tests**: End-to-end process testing
- **Component Interaction Tests**: Cross-component communication
- **Data Flow Tests**: Data processing pipeline testing

### Functional Tests
- **Feature Tests**: Complete feature functionality
- **User Scenario Tests**: Real-world usage scenarios
- **Performance Tests**: System performance and load testing

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run with coverage
python run_tests.py --coverage

# Run tests in parallel
python run_tests.py --parallel
```

### Specific Test Categories
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Functional tests only
python run_tests.py --functional

# Performance tests only
python run_tests.py --performance
```

### Individual Test Files
```bash
# Run specific test file
python -m pytest tests/test_analyzer.py

# Run specific test function
python -m pytest tests/test_analyzer.py::test_pdf_analysis

# Run tests with specific marker
python -m pytest -m "slow"
```

## 📊 Test Coverage

### Coverage Targets
- **Overall Coverage**: 80% minimum
- **Critical Components**: 90% minimum
- **UI Components**: 70% minimum
- **Utility Functions**: 85% minimum

### Coverage Reports
```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View coverage report
open htmlcov/index.html
```

## 🎯 Test Components

### Analyzer Tests (`test_analyzer.py`)
- PDF text extraction accuracy
- Terminology detection precision
- Quantity extraction validation
- Error handling and edge cases
- Performance benchmarks

### Bid Engine Tests (`test_bid_engine.py`)
- Bid generation accuracy
- Pricing calculation validation
- Line item creation testing
- Template processing verification
- Export format testing

### Extractor Tests (`test_extractor.py`)
- Catalog data extraction
- Table parsing accuracy
- Product information validation
- Error handling for corrupted files
- Performance with large files

### Product Matcher Tests (`test_product_matcher.py`)
- Fuzzy matching algorithms
- Confidence scoring accuracy
- Multi-agency terminology support
- Alternative product suggestions
- Matching performance optimization

### UI Component Tests (`test_ui_components.py`)
- Component rendering
- User interaction handling
- State management
- Error display
- Responsive design testing

## 🔧 Test Configuration

### Pytest Configuration (`conftest.py`)
```python
# Shared fixtures
@pytest.fixture
def sample_pdf_file():
    """Provide sample PDF for testing."""
    return "tests/data/sample_project.pdf"

@pytest.fixture
def sample_catalog_data():
    """Provide sample catalog data."""
    return load_test_catalog_data()

@pytest.fixture
def mock_analysis_result():
    """Provide mock analysis result."""
    return create_mock_analysis_result()
```

### Test Data
```
tests/
├── data/                    # Test data files
│   ├── sample_project.pdf   # Sample project PDF
│   ├── sample_catalog.pdf   # Sample catalog PDF
│   ├── test_products.json   # Test product data
│   └── expected_results/    # Expected test results
└── fixtures/               # Test fixtures
    ├── analysis_results.py # Analysis result fixtures
    ├── bid_data.py         # Bid data fixtures
    └── catalog_data.py     # Catalog data fixtures
```

## 🎨 Test Markers

### Available Markers
```python
# Test categories
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.functional     # Functional tests
@pytest.mark.performance    # Performance tests

# Test characteristics
@pytest.mark.slow          # Slow running tests
@pytest.mark.fast          # Fast running tests
@pytest.mark.critical      # Critical functionality
@pytest.mark.optional      # Optional features

# Agency-specific tests
@pytest.mark.caltrans      # CalTrans-specific tests
@pytest.mark.dot           # DOT agency tests
@pytest.mark.municipal     # Municipal tests
@pytest.mark.federal       # Federal tests
@pytest.mark.commercial    # Commercial tests
```

### Running Marked Tests
```bash
# Run only fast tests
python -m pytest -m "fast"

# Run critical tests
python -m pytest -m "critical"

# Run CalTrans-specific tests
python -m pytest -m "caltrans"

# Exclude slow tests
python -m pytest -m "not slow"
```

## 🚨 Test Environment

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-xdist pytest-html

# Install development dependencies
pip install -r requirements-dev.txt
```

### Environment Setup
```bash
# Set test environment
export TESTING=True
export TEST_DATA_PATH=tests/data
export TEST_OUTPUT_PATH=tests/output

# Run environment check
python run_tests.py --check
```

## 📈 Performance Testing

### Load Testing
```bash
# Run performance tests
python run_tests.py --performance

# Test with large files
python -m pytest tests/test_performance.py::test_large_pdf_processing

# Test concurrent processing
python -m pytest tests/test_performance.py::test_concurrent_analysis
```

### Benchmark Tests
- **File Processing Speed**: PDF analysis time
- **Memory Usage**: Peak memory consumption
- **Concurrent Users**: Multi-user simulation
- **Database Performance**: Query optimization

## 🔍 Debugging Tests

### Verbose Output
```bash
# Maximum verbosity
python -m pytest -vvv tests/test_analyzer.py

# Show local variables on failure
python -m pytest -l tests/test_analyzer.py

# Show captured output
python -m pytest -s tests/test_analyzer.py
```

### Test Debugging
```python
# Add debugging to tests
def test_debug_example():
    import pdb; pdb.set_trace()  # Debugger breakpoint
    result = analyzer.analyze_pdf("test.pdf")
    assert result is not None
```

### Logging
```bash
# Run tests with logging
python -m pytest --log-cli-level=DEBUG tests/test_analyzer.py

# Save test logs
python -m pytest --log-file=test.log tests/
```

## 📊 Test Reporting

### HTML Reports
```bash
# Generate HTML test report
python -m pytest --html=test_report.html --self-contained-html

# View report
open test_report.html
```

### JUnit XML
```bash
# Generate JUnit XML report
python -m pytest --junitxml=test_results.xml

# For CI/CD integration
python -m pytest --junitxml=test-results.xml --cov=src --cov-report=xml
```

## 🚀 Continuous Integration

### GitHub Actions
```yaml
# .github/workflows/tests.yml
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
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --coverage
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest
        language: system
        pass_filenames: false
```

## 📞 Support

### Test Issues
- Check test environment setup
- Review test data and fixtures
- Verify dependencies are installed
- Check for environment-specific issues

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Use descriptive test function names
4. Add appropriate markers
5. Include docstrings and comments
6. Update this README if needed

## 📄 License

This test suite is part of PACE - Project Analysis & Construction Estimating and follows the same licensing terms as the main project.

---

**Made with ❤️ for the construction industry** 