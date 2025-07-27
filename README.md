# CalTrans Bidding System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47.1+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive **Streamlit-based web application** for automating CalTrans bidding processes. This system combines PDF analysis, catalog extraction, and intelligent bid generation to streamline construction project bidding workflows.

## 🏗️ Project Overview

The CalTrans Bidding System is designed to revolutionize how construction companies approach CalTrans project bidding by providing:

### ✨ Key Features

- **📚 Intelligent Catalog Extraction**: Automatically extract and process Whitecap catalog PDFs
- **🔍 Advanced PDF Analysis**: Parse CalTrans project documents with terminology detection
- **💰 Automated Bid Generation**: Create professional bid packages with pricing calculations
- **📊 Real-time Analytics**: Dashboard with project metrics and system status
- **📄 Multi-format Export**: Export bids as Excel, JSON, or email reports
- **⚙️ Configurable Settings**: Customizable markup rates, tax calculations, and delivery fees
- **🔄 Batch Processing**: Handle multiple projects simultaneously
- **📈 Progress Tracking**: Real-time progress indicators and validation

### 🎯 Use Cases

- **Construction Companies**: Streamline CalTrans project bidding
- **Contractors**: Automate catalog processing and bid generation
- **Project Managers**: Track multiple bids and project status
- **Estimators**: Generate accurate cost estimates with built-in calculations

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/caltrans-bidding-system.git
   cd caltrans-bidding-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import streamlit; print('Installation successful!')"
   ```

### 🐳 Docker Installation (Alternative)

```bash
# Build the Docker image
docker build -t caltrans-bidding-system .

# Run the application
docker run -p 8501:8501 caltrans-bidding-system
```

## 📖 Usage Guide

### 🏠 Getting Started

1. **Launch the application**
   ```bash
   streamlit run main.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8501`

3. **Welcome to the Dashboard**
   ![Dashboard](docs/images/dashboard.png)

### 📚 Extract Catalog

1. **Navigate to "Extract Catalog"**
   - Click on the sidebar navigation
   - Upload your Whitecap catalog PDF

2. **Process the catalog**
   - The system will automatically extract product information
   - View extraction progress in real-time
   - Review extracted data in the preview section

3. **Export results**
   - Download as Excel spreadsheet
   - Export as JSON for API integration
   - Email catalog data to team members

![Catalog Extraction](docs/images/catalog-extraction.png)

### 🔍 Analyze CalTrans PDF

1. **Upload project documents**
   - Navigate to "Analyze CalTrans PDF"
   - Upload CalTrans project PDFs
   - Support for multiple file formats

2. **Review analysis results**
   - View extracted terminology and quantities
   - Check for critical alerts and warnings
   - Review lumber requirements calculations

3. **Export analysis**
   - Generate detailed analysis reports
   - Compare multiple project analyses
   - Export findings for team review

![PDF Analysis](docs/images/pdf-analysis.png)

### 💰 Generate Bid

1. **Prerequisites check**
   - Ensure catalog data is loaded
   - Verify PDF analysis is complete
   - Configure bid settings

2. **Generate bid package**
   - Automatic line item creation
   - Pricing calculations with markup
   - Delivery fee calculations
   - Waste factor adjustments

3. **Review and export**
   - Validate bid accuracy
   - Export as professional Excel bid
   - Generate summary reports

![Bid Generation](docs/images/bid-generation.png)

### ⚙️ Settings Configuration

1. **System Configuration**
   - Set default markup percentages
   - Configure tax rates
   - Choose default currency

2. **Email Settings**
   - Configure SMTP server settings
   - Set up email notifications
   - Manage recipient lists

3. **Data Management**
   - Clear upload history
   - Export system data
   - Backup and restore settings

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
DEFAULT_MARKUP=20.0
DEFAULT_TAX_RATE=8.25
DEFAULT_CURRENCY=USD

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your@email.com
EMAIL_PASSWORD=your_app_password

# File Paths
CATALOG_OUTPUT_PATH=output/catalogs/
BID_OUTPUT_PATH=output/bids/
TEMP_DIR=temp/

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Configuration Files

#### `config/settings.py`
```python
# Default application settings
DEFAULT_SETTINGS = {
    'markup_percentage': 20.0,
    'tax_rate': 8.25,
    'delivery_fee_percentage': 3.0,
    'delivery_fee_minimum': 150.0,
    'waste_factors': {
        'formwork': 0.10,
        'lumber': 0.10,
        'hardware': 0.05,
        'specialty': 0.15
    }
}
```

#### `config/catalog_sections.json`
```json
{
  "concrete_forming": {
    "start_page": 1,
    "end_page": 50,
    "priority": "high"
  },
  "fastening_systems": {
    "start_page": 51,
    "end_page": 100,
    "priority": "medium"
  }
}
```

## 🛠️ Troubleshooting Guide

### Common Issues

#### 1. **PDF Upload Fails**
```
Error: "Failed to upload PDF file"
```

**Solution:**
- Ensure PDF is not password-protected
- Check file size (max 200MB)
- Verify PDF is not corrupted
- Try converting to PDF/A format

#### 2. **Catalog Extraction Issues**
```
Error: "No products found in catalog"
```

**Solution:**
- Verify Whitecap catalog format
- Check if PDF contains tables
- Ensure catalog is not scanned images
- Try different extraction settings

#### 3. **Bid Generation Errors**
```
Error: "Prerequisites not met"
```

**Solution:**
- Complete catalog extraction first
- Analyze CalTrans PDF before generating bid
- Check system status in sidebar
- Verify all required data is loaded

#### 4. **Performance Issues**
```
Error: "Application running slowly"
```

**Solution:**
- Close other applications
- Increase system memory allocation
- Use smaller PDF files
- Enable batch processing for large files

### Log Files

Check log files for detailed error information:

```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log

# View system logs
tail -f logs/system.log
```

### System Requirements

- **Minimum:**
  - 4GB RAM
  - 2GB free disk space
  - Python 3.8+

- **Recommended:**
  - 8GB RAM
  - 5GB free disk space
  - Python 3.9+
  - SSD storage

## 📚 API Documentation

### Core Classes

#### `CalTransPDFAnalyzer`
Main class for analyzing CalTrans project PDFs.

```python
from src.analyzers.caltrans_analyzer import CalTransPDFAnalyzer

# Initialize analyzer
analyzer = CalTransPDFAnalyzer()

# Analyze PDF
result = analyzer.analyze_pdf("project.pdf")

# Access results
print(f"Found {len(result.terminology_found)} terms")
print(f"Extracted {len(result.quantities)} quantities")
```

#### `WhitecapCatalogExtractor`
Extracts product data from Whitecap catalog PDFs.

```python
from src.extractors.whitecap_extractor import WhitecapCatalogExtractor

# Initialize extractor
extractor = WhitecapCatalogExtractor()

# Extract catalog data
catalog_data = extractor.extract_catalog_data("catalog.pdf")

# Export to CSV
extractor.export_to_csv(catalog_data, "products.csv")
```

#### `CalTransBiddingEngine`
Generates complete bid packages.

```python
from src.bidding.bid_engine import CalTransBiddingEngine

# Initialize bidding engine
engine = CalTransBiddingEngine()

# Generate complete bid
bid_package = engine.generate_complete_bid(
    pdf_path="project.pdf",
    project_name="Highway 101 Bridge",
    project_number="CT-2024-001",
    markup_percentage=20.0
)
```

### Data Structures

#### `CalTransAnalysisResult`
```python
@dataclass
class CalTransAnalysisResult:
    pdf_path: str
    analysis_timestamp: datetime
    total_pages: int
    terminology_found: List[TermMatch]
    quantities: List[ExtractedQuantity]
    alerts: List[Alert]
    lumber_requirements: LumberRequirements
```

#### `BidPackage`
```python
@dataclass
class BidPackage:
    project_name: str
    project_number: str
    bid_date: datetime
    line_items: List[BidLineItem]
    pricing_summary: PricingSummary
    markup_percentage: float
```

### Utility Functions

#### Data Validation
```python
from src.utils.data_validator import DataValidator

validator = DataValidator()
result = validator.validate_catalog_data(catalog_df)
```

#### Excel Generation
```python
from src.utils.excel_generator import ExcelBidGenerator

generator = ExcelBidGenerator()
generator.generate_bid_excel(bid_package, "output/bid.xlsx")
```

## 🤝 Contributing Guidelines

We welcome contributions! Please follow these guidelines:

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python run_tests.py
   ```
5. **Submit a pull request**

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add docstrings to all classes and methods
- Keep functions under 50 lines
- Use meaningful variable names

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting
- Add integration tests for complex workflows
- Test with different PDF formats

### Documentation

- Update README.md for new features
- Add inline code comments
- Update API documentation
- Include usage examples

### Commit Messages

Use conventional commit format:
```
feat: add new catalog extraction feature
fix: resolve PDF upload issue
docs: update installation instructions
test: add unit tests for bid engine
```

## 📄 License Information

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### License Summary

- **Commercial Use**: ✅ Allowed
- **Modification**: ✅ Allowed
- **Distribution**: ✅ Allowed
- **Private Use**: ✅ Allowed
- **Liability**: ❌ No warranty provided

### Third-Party Licenses

This project uses the following third-party libraries:

- **Streamlit**: Apache 2.0 License
- **pdfplumber**: MIT License
- **pandas**: BSD 3-Clause License
- **plotly**: MIT License
- **fuzzywuzzy**: GPL v2 License

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

### Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/yourusername/caltrans-bidding-system/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/yourusername/caltrans-bidding-system/discussions)
- **Wiki**: [Additional documentation and tutorials](https://github.com/yourusername/caltrans-bidding-system/wiki)

## 🔄 Changelog

### Version 1.0.0 (2024-01-15)
- Initial release
- PDF analysis capabilities
- Catalog extraction
- Bid generation engine
- Streamlit web interface

### Version 1.1.0 (Planned)
- Enhanced PDF processing
- Additional export formats
- Performance improvements
- Mobile-responsive UI

## 🙏 Acknowledgments

- **CalTrans**: For project specifications and requirements
- **Whitecap**: For product catalog data
- **Streamlit**: For the excellent web framework
- **Open Source Community**: For the amazing libraries used in this project

---

**Made with ❤️ for the construction industry** 