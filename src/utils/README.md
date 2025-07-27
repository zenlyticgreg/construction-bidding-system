# Utils Module Documentation

This directory contains utility modules for the CalTrans bidding system, including Excel generation and comprehensive reporting capabilities.

## Modules

### 1. Excel Generator Module

The Excel Generator module provides comprehensive functionality to create professional Excel bid documents with multiple sheets, professional formatting, and comprehensive styling.

#### Features

- **Professional Formatting**: Company branding, color scheme, consistent styling
- **Multiple Sheets**: Executive Summary, Line Items Detail, CalTrans Analysis
- **Business Ready**: Currency formatting, auto-adjusted columns, error handling

#### Quick Start

```python
from src.utils.excel_generator import ExcelBidGenerator

generator = ExcelBidGenerator("Your Company Name")
excel_bytes = generator.create_professional_bid(bid_data)
```

[See full Excel Generator documentation below](#excel-generator-module)

---

### 2. Report Generator Module

The Report Generator module provides comprehensive reporting capabilities for the CalTrans bidding system, including extraction summaries, bid analysis, project comparisons, and management dashboards.

#### Features

- **Multiple Report Types**: Extraction summaries, bid analysis, project comparisons, management dashboards
- **Professional Formatting**: HTML templates with company branding and consistent styling
- **Multiple Export Formats**: HTML, JSON, and text formats
- **Comprehensive Metrics**: Key performance indicators and trend analysis
- **Error Handling**: Robust error handling and logging
- **Streamlit Integration**: Ready for web application deployment

#### Quick Start

```python
from src.utils.report_generator import ReportGenerator

generator = ReportGenerator("Your Company Name")
report_html = generator.generate_extraction_summary(extraction_data)
```

[See full Report Generator documentation below](#report-generator-module)

---

## Excel Generator Module

### Features

#### 🎨 Professional Formatting
- **Company Branding**: Customizable company name and optional logo integration
- **Color Scheme**: Professional dark blue (#1F4E79) header with white text
- **Consistent Styling**: Named styles for headers, data, currency, and numbers
- **Auto-adjusted Columns**: Intelligent column width adjustment based on content

#### 📊 Multiple Sheets
1. **Executive Summary**: Project information, pricing summary, and bid notes
2. **Line Items Detail**: Itemized product list with quantities, pricing, and totals
3. **CalTrans Analysis**: Terms found, confidence scores, and alerts/warnings

#### 💼 Business Ready Features
- **Currency Formatting**: Automatic $#,##0.00 formatting for monetary values
- **Number Formatting**: Proper formatting for quantities and percentages
- **Professional Borders**: Consistent border styling throughout
- **Error Handling**: Comprehensive error handling and logging

### Installation

The Excel Generator uses `openpyxl` which is already included in the project requirements:

```bash
pip install openpyxl
```

### Quick Start

#### Basic Usage

```python
from src.utils.excel_generator import ExcelBidGenerator

# Create generator instance
generator = ExcelBidGenerator("Your Company Name")

# Prepare bid data
bid_data = {
    'project_info': {
        'project_name': 'CalTrans Highway Project',
        'project_number': 'CT-2024-001',
        'contact_person': 'John Smith',
        'phone': '(555) 123-4567',
        'email': 'john@company.com'
    },
    'line_items': [
        {
            'sku': 'CT-001',
            'description': 'Traffic Cone - 28" Orange',
            'quantity': 100,
            'unit_price': 12.50,
            'extended_price': 1250.00,
            'notes': 'High visibility safety equipment'
        }
    ],
    'caltrans_analysis': {
        'total_terms': 15,
        'matched_products': 12,
        'confidence_score': 0.85,
        'terms_found': [...],
        'alerts': [...]
    },
    'pricing_summary': {
        'subtotal': 3312.50,
        'tax_rate': 0.085,
        'tax_amount': 281.56,
        'total': 3819.06
    },
    'notes': 'All items meet CalTrans specifications.'
}

# Generate Excel file
excel_bytes = generator.create_professional_bid(bid_data)
```

#### Streamlit Integration

```python
import streamlit as st
from src.utils.excel_generator import ExcelBidGenerator

# Create download button in Streamlit
if st.button("Generate Excel"):
    generator = ExcelBidGenerator("Your Company")
    excel_bytes = generator.create_professional_bid(bid_data)
    
    st.download_button(
        label="Download Excel",
        data=excel_bytes,
        file_name="bid_document.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

### API Reference

#### ExcelBidGenerator Class

##### Constructor

```python
ExcelBidGenerator(company_name: str = "Zenlytic Solutions", 
                 company_logo_path: Optional[str] = None)
```

**Parameters:**
- `company_name`: Company name for branding (default: "Zenlytic Solutions")
- `company_logo_path`: Optional path to company logo image

##### Methods

###### `create_professional_bid(bid_data: Dict[str, Any]) -> bytes`

Creates a complete professional Excel bid document.

**Parameters:**
- `bid_data`: Dictionary containing bid information

**Returns:**
- `bytes`: Excel file as bytes for download

###### `create_summary_sheet(wb: Workbook, bid_data: Dict[str, Any]) -> None`

Creates the Executive Summary sheet.

###### `create_line_items_sheet(wb: Workbook, bid_data: Dict[str, Any]) -> None`

Creates the Line Items Detail sheet.

###### `create_analysis_sheet(wb: Workbook, bid_data: Dict[str, Any]) -> None`

Creates the CalTrans Analysis sheet.

### Testing

Run the test script to verify functionality:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the example
python src/utils/excel_generator.py
```

This will create a `sample_bid.xlsx` file for inspection.

---

## Report Generator Module

### Features

#### 📊 Multiple Report Types
- **Extraction Summaries**: Document processing results and metrics
- **Bid Analysis Reports**: Detailed bid data and pricing analysis
- **Project Comparisons**: Multi-project analysis and trend identification
- **Management Dashboards**: Executive-level metrics and KPIs
- **Performance Reports**: System performance tracking and analysis

#### 🎨 Professional Formatting
- **HTML Templates**: Professional styling with company branding
- **Responsive Design**: Mobile-friendly report layouts
- **Consistent Styling**: Unified color scheme and typography
- **Interactive Elements**: Charts and visualizations where applicable

#### 📁 Multiple Export Formats
- **HTML**: Web-ready reports with embedded styling
- **JSON**: Structured data for API integration
- **Text**: Plain text format for simple reports

#### 📈 Comprehensive Analytics
- **Key Performance Indicators**: Extraction accuracy, processing time, success rates
- **Trend Analysis**: Historical data analysis and forecasting
- **Comparative Analysis**: Multi-project comparisons and benchmarking
- **Recommendations**: AI-powered insights and suggestions

### Installation

The Report Generator uses several dependencies that are included in the project requirements:

```bash
pip install jinja2 matplotlib seaborn pandas plotly
```

### Quick Start

#### Basic Usage

```python
from src.utils.report_generator import ReportGenerator

# Create generator instance
generator = ReportGenerator("Your Company Name")

# Generate extraction summary
extraction_data = {
    'total_pages': 15,
    'total_terms': 127,
    'extraction_time': 45.2,
    'confidence_score': 0.87,
    'terms_breakdown': {...},
    'errors': [...],
    'warnings': [...]
}

report_html = generator.generate_extraction_summary(extraction_data)
```

#### Streamlit Integration

```python
import streamlit as st
from src.utils.report_generator import ReportGenerator

# Create report generator
generator = ReportGenerator("Your Company")

# Generate and download report
if st.button("Generate Report"):
    report_html = generator.generate_extraction_summary(extraction_data)
    
    st.download_button(
        label="Download Report",
        data=report_html,
        file_name="extraction_report.html",
        mime="text/html"
    )
```

### API Reference

#### ReportGenerator Class

##### Constructor

```python
ReportGenerator(company_name: str = "Zenlytic Solutions", 
               output_dir: str = "output/reports")
```

**Parameters:**
- `company_name`: Company name for branding
- `output_dir`: Directory for saving reports

##### Methods

###### `generate_extraction_summary(extraction_results: Dict[str, Any]) -> str`

Generate a summary report of extraction results.

**Parameters:**
- `extraction_results`: Dictionary containing extraction data

**Returns:**
- `str`: HTML formatted extraction summary report

###### `generate_bid_analysis_report(bid_data: Dict[str, Any]) -> str`

Generate a comprehensive bid analysis report.

**Parameters:**
- `bid_data`: Dictionary containing bid information

**Returns:**
- `str`: HTML formatted bid analysis report

###### `create_project_comparison(project_list: List[Dict[str, Any]]) -> Dict[str, Any]`

Create a project comparison analysis.

**Parameters:**
- `project_list`: List of project dictionaries

**Returns:**
- `Dict`: Comparison analysis results with statistics and trends

###### `export_management_dashboard(data: Dict[str, Any]) -> bytes`

Export a management dashboard with charts and metrics.

**Parameters:**
- `data`: Dictionary containing dashboard data

**Returns:**
- `bytes`: HTML dashboard as bytes

###### `generate_performance_report(performance_data: Dict[str, Any]) -> str`

Generate a performance tracking report.

**Parameters:**
- `performance_data`: Dictionary containing performance metrics

**Returns:**
- `str`: HTML formatted performance report

###### `save_report(report_content: str, filename: str, format_type: str = 'html') -> str`

Save report to file.

**Parameters:**
- `report_content`: Report content
- `filename`: Output filename
- `format_type`: Output format (html, json, txt)

**Returns:**
- `str`: Path to saved file

### Report Types

#### 1. Extraction Summary Report

**Purpose**: Summarize document extraction and processing results

**Key Metrics**:
- Pages processed
- Terms extracted
- Processing time
- Confidence scores
- Error and warning counts

**Sample Data Structure**:
```python
{
    'total_pages': 15,
    'total_terms': 127,
    'extraction_time': 45.2,
    'confidence_score': 0.87,
    'terms_breakdown': {
        'Safety Equipment': 45,
        'Construction Materials': 32,
        'Tools': 28,
        'Signage': 22
    },
    'errors': ['Low resolution image on page 7'],
    'warnings': ['Multiple similar terms detected']
}
```

#### 2. Bid Analysis Report

**Purpose**: Analyze bid data, pricing, and project information

**Key Sections**:
- Project overview
- Pricing analysis
- Line items breakdown
- CalTrans analysis summary

**Sample Data Structure**:
```python
{
    'project_info': {
        'project_name': 'CalTrans Highway Project',
        'project_number': 'CT-2024-001',
        'contact_person': 'John Smith',
        'phone': '(555) 123-4567',
        'email': 'john@company.com'
    },
    'line_items': [...],
    'pricing_summary': {
        'subtotal': 3312.50,
        'tax_amount': 281.56,
        'total': 3819.06
    },
    'caltrans_analysis': {
        'total_terms': 15,
        'matched_products': 12,
        'confidence_score': 0.85
    }
}
```

#### 3. Project Comparison Report

**Purpose**: Compare multiple projects and identify trends

**Key Features**:
- Statistical analysis
- Trend identification
- Performance benchmarking
- Recommendations

**Sample Data Structure**:
```python
[
    {
        'project_name': 'Project A',
        'total_bid': 100000,
        'confidence_score': 0.85,
        'bid_date': '2024-01-15',
        'status': 'Won'
    },
    {
        'project_name': 'Project B',
        'total_bid': 120000,
        'confidence_score': 0.90,
        'bid_date': '2024-02-01',
        'status': 'Pending'
    }
]
```

#### 4. Management Dashboard

**Purpose**: Executive-level overview of system performance

**Key Metrics**:
- Total projects
- Average bid amounts
- Success rates
- Revenue tracking
- Performance trends

**Sample Data Structure**:
```python
{
    'metrics': {
        'total_projects': 45,
        'avg_bid_amount': 125000,
        'success_rate': 0.78,
        'total_revenue': 5625000
    },
    'projects': [...],
    'trends': {
        'bid_amount_trend': {'direction': 'increasing', 'value': 0.15},
        'confidence_trend': {'direction': 'improving', 'value': 0.08}
    }
}
```

#### 5. Performance Report

**Purpose**: Track system performance and operational metrics

**Key Categories**:
- Accuracy metrics
- Time metrics
- Cost metrics

**Sample Data Structure**:
```python
{
    'accuracy_metrics': {
        'extraction_accuracy': 0.87,
        'matching_accuracy': 0.92,
        'overall_confidence': 0.89
    },
    'time_metrics': {
        'avg_processing_time': 2.5,
        'fastest_processing': 1.2,
        'slowest_processing': 4.8
    },
    'cost_metrics': {
        'avg_cost_per_project': 1250.00,
        'total_operational_cost': 56250.00,
        'cost_savings': 18750.00
    }
}
```

### Styling and Formatting

#### Color Scheme
- **Primary**: #1F4E79 (Dark Blue)
- **Secondary**: #4472C4 (Medium Blue)
- **Accent**: #D9E2F3 (Light Blue)
- **Success**: #28A745 (Green)
- **Warning**: #FFC107 (Yellow)
- **Danger**: #DC3545 (Red)
- **Info**: #17A2B8 (Cyan)

#### HTML Template Features
- **Responsive Design**: Mobile-friendly layouts
- **Professional Styling**: Clean, modern appearance
- **Company Branding**: Customizable headers and footers
- **Metric Cards**: Highlighted key performance indicators
- **Data Tables**: Structured information presentation
- **Charts and Visualizations**: Interactive data representation

### Error Handling

The module includes comprehensive error handling:

- **Data Validation**: Input validation and type checking
- **Graceful Degradation**: Fallback options for missing data
- **Detailed Logging**: Comprehensive error logging and debugging
- **User-Friendly Messages**: Clear error messages for end users
- **Recovery Mechanisms**: Automatic retry and recovery options

### Examples

#### Complete Example

See `examples/report_generator_example.py` for a complete Streamlit integration example.

#### Sample Data Functions

Use the provided sample data functions for testing:

```python
from src.utils.report_generator import (
    create_sample_extraction_data,
    create_sample_bid_data,
    create_sample_dashboard_data
)

# Generate sample data
extraction_data = create_sample_extraction_data()
bid_data = create_sample_bid_data()
dashboard_data = create_sample_dashboard_data()
```

### Integration with CalTrans Bidding System

The Report Generator integrates seamlessly with the existing CalTrans bidding system:

1. **Extraction Integration**: Use with `src/extractors/whitecap_extractor.py` output
2. **Analysis Integration**: Incorporate results from `src/analyzers/caltrans_analyzer.py`
3. **Bidding Integration**: Use with `src/bidding/bid_engine.py` output
4. **Product Matching**: Include results from `src/analyzers/product_matcher.py`

#### Typical Workflow

```python
from src.extractors.whitecap_extractor import WhitecapExtractor
from src.analyzers.caltrans_analyzer import CalTransAnalyzer
from src.bidding.bid_engine import BidEngine
from src.utils.report_generator import ReportGenerator

# Extract data from documents
extractor = WhitecapExtractor()
extraction_results = extractor.extract_document(pdf_path)

# Analyze CalTrans requirements
analyzer = CalTransAnalyzer()
analysis_results = analyzer.analyze_document(extraction_results)

# Generate bid
bid_engine = BidEngine()
bid_results = bid_engine.generate_bid(analysis_results)

# Create reports
generator = ReportGenerator("Your Company")

# Generate extraction summary
extraction_report = generator.generate_extraction_summary(extraction_results)

# Generate bid analysis
bid_report = generator.generate_bid_analysis_report(bid_results)

# Create project comparison
comparison = generator.create_project_comparison([bid_results])

# Export management dashboard
dashboard = generator.export_management_dashboard({
    'metrics': {...},
    'projects': [bid_results],
    'trends': {...}
})
```

### Testing

Run the test script to verify functionality:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the example
python src/utils/report_generator.py
```

This will create sample reports in the `output/reports` directory.

### Dependencies

- `jinja2>=3.1.6`: HTML template rendering
- `matplotlib>=3.10.3`: Chart generation and visualization
- `seaborn>=0.13.2`: Statistical data visualization
- `pandas>=2.3.1`: Data manipulation and analysis
- `plotly>=6.2.0`: Interactive charts and dashboards
- `datetime`: Date/time handling
- `logging`: Error logging and debugging
- `typing`: Type hints for better code documentation

### Contributing

When contributing to the Report Generator:

1. Maintain consistent styling and formatting
2. Add comprehensive error handling
3. Include type hints for all functions
4. Update documentation for new features
5. Test with various data structures
6. Ensure responsive design for all reports
7. Follow accessibility guidelines

### License

This module is part of the CalTrans Bidding System and follows the same licensing terms. 