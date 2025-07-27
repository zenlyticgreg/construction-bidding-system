# CalTrans PDF Analyzer

A comprehensive PDF analysis tool specifically designed for CalTrans construction projects. This analyzer extracts terminology, quantities, and calculates material requirements from CalTrans project PDFs.

## Features

### Core Analysis Capabilities
- **Terminology Detection**: Identifies CalTrans-specific construction terms using fuzzy matching
- **Quantity Extraction**: Extracts quantities using regex patterns (SQFT, LF, CY, EA, TON, GAL, LB)
- **High-Priority Term Identification**: Flags critical construction items for attention
- **Lumber Requirement Calculations**: Calculates formwork and material requirements
- **Alert Generation**: Creates alerts for high-value items and large quantities
- **Context Extraction**: Provides surrounding context for found terms and quantities

### Key Terms Detected
- **Bridge & Railing**: BALUSTER, TYPE_86H_RAIL
- **Formwork**: BLOCKOUT, FORM_FACING, FALSEWORK, STRIPPING, WALING
- **Concrete**: STAMPED_CONCRETE, FRACTURED_RIB_TEXTURE, RETAINING_WALL
- **Temporary Structures**: EROSION_CONTROL, CRIBBING
- **Architectural**: ARCHITECTURAL_TREATMENT

### Quantity Units Supported
- **SQFT**: Square feet, square yards, square meters
- **LF**: Linear feet, linear yards, linear meters
- **CY**: Cubic yards, cubic feet, cubic meters
- **EA**: Each, pieces, units
- **TON**: Tons
- **GAL**: Gallons
- **LB**: Pounds

## Installation

1. Ensure you have the required dependencies:
```bash
pip install -r requirements.txt
```

2. The analyzer requires the CalTrans reference data:
```bash
# Reference data should be in data/caltrans_reference.json
```

## Usage

### Basic Usage

```python
from analyzers.caltrans_analyzer import CalTransPDFAnalyzer

# Initialize analyzer
analyzer = CalTransPDFAnalyzer()

# Analyze a PDF file
result = analyzer.analyze_pdf("path/to/caltrans_project.pdf")

# Access results
print(f"Found {len(result.terminology_found)} terms")
print(f"Extracted {len(result.quantities)} quantities")
print(f"Generated {len(result.alerts)} alerts")
```

### Convenience Functions

```python
from analyzers.caltrans_analyzer import (
    analyze_caltrans_pdf,
    extract_quantities_from_text,
    find_caltrans_terms
)

# Quick PDF analysis
result = analyze_caltrans_pdf("project.pdf")

# Extract quantities from text
quantities = extract_quantities_from_text("Concrete: 500 CY, Formwork: 2000 SQFT")

# Find CalTrans terms in text
terms = find_caltrans_terms("BALUSTER installation for bridge railing")
```

## Data Structures

### CalTransAnalysisResult
Complete analysis result containing:
- `terminology_found`: List of found CalTrans terms
- `quantities`: List of extracted quantities
- `alerts`: List of generated alerts
- `sheet_analyses`: Page-by-page analysis results
- `total_lumber_requirements`: Calculated lumber requirements
- `high_priority_terms`: Count of high-priority terms
- `total_quantities`: Count of extracted quantities
- `critical_alerts`: Count of critical alerts

### TermMatch
Represents a found CalTrans term:
- `term`: The found term
- `category`: Term category (bridge_barrier, formwork, etc.)
- `priority`: Priority level (high, medium, low)
- `context`: Surrounding text context
- `page_number`: Page where term was found
- `confidence`: Detection confidence score
- `quantities`: Associated quantities

### ExtractedQuantity
Represents an extracted quantity:
- `value`: Numeric quantity value
- `unit`: Unit of measurement
- `context`: Surrounding text context
- `page_number`: Page where quantity was found
- `confidence`: Extraction confidence score
- `term_associated`: Associated CalTrans term

### Alert
Represents an analysis alert:
- `level`: Alert level (info, warning, high, critical)
- `message`: Alert message
- `term`: Associated term (if applicable)
- `quantity`: Associated quantity (if applicable)
- `page_number`: Page where alert was generated

### LumberRequirements
Calculated lumber requirements:
- `total_board_feet`: Total board feet required
- `plywood_sheets`: Number of plywood sheets
- `dimensional_lumber`: Breakdown by lumber size
- `formwork_area`: Total formwork area
- `estimated_cost`: Estimated material and labor cost

## Configuration

### CalTrans Reference Data
The analyzer uses `data/caltrans_reference.json` for:
- Term definitions and categories
- Regex patterns for quantity extraction
- Alert thresholds and triggers
- Material calculation constants
- Production rates and factors

### Customization
You can customize the analyzer by:
1. Modifying the reference JSON file
2. Extending the regex patterns
3. Adjusting alert thresholds
4. Adding new term categories

## Alert System

### Alert Levels
- **INFO**: General information about found items
- **WARNING**: Items requiring attention
- **HIGH**: High-value or critical items
- **CRITICAL**: Items requiring immediate attention

### Alert Triggers
- High-priority terms detected
- Large quantities exceeding thresholds
- Missing critical information
- Quality issues in text extraction

## Lumber Calculations

### Calculation Factors
- **Formwork Area**: Based on extracted SQFT quantities
- **Plywood Sheets**: Calculated from formwork area
- **Dimensional Lumber**: Estimated based on typical usage
- **Waste Factor**: 15% default waste allowance
- **Reuse Factor**: 3x reuse for plywood, 5x for lumber

### Cost Estimation
- Material costs from reference data
- Labor costs based on production rates
- Overhead and profit margins
- Delivery and handling costs

## Error Handling

The analyzer includes comprehensive error handling:
- Graceful handling of missing reference data
- Fallback patterns when JSON is unavailable
- Robust text extraction with quality scoring
- Detailed logging for debugging

## Testing

Run the test suite to verify functionality:

```bash
python tests/test_caltrans_analyzer.py
```

The test suite includes:
- Quantity extraction tests
- Term detection tests
- Lumber calculation tests
- Alert generation tests
- Context extraction tests
- Full integration tests

## Performance

### Optimization Features
- Compiled regex patterns for fast matching
- Fuzzy matching with configurable thresholds
- Efficient text processing algorithms
- Caching of reference data

### Typical Performance
- Small PDFs (< 10 pages): < 5 seconds
- Medium PDFs (10-50 pages): 5-30 seconds
- Large PDFs (50+ pages): 30+ seconds

## Integration

### With Bidding System
The analyzer integrates with the CalTrans bidding system:
- Provides structured data for bid preparation
- Identifies high-value items for pricing
- Calculates material requirements
- Generates alerts for review

### With Other Tools
- Exports results in JSON format
- Compatible with data validation utilities
- Integrates with logging systems
- Supports custom output formats

## Troubleshooting

### Common Issues
1. **Missing Reference Data**: Ensure `caltrans_reference.json` exists
2. **Import Errors**: Check virtual environment and dependencies
3. **JSON Syntax Errors**: Validate reference file format
4. **Text Extraction Issues**: Check PDF quality and format

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger("caltrans_analyzer").setLevel(logging.DEBUG)
```

## Contributing

To extend the analyzer:
1. Add new terms to the reference JSON
2. Extend regex patterns for new quantity formats
3. Add new alert triggers
4. Implement additional calculation methods
5. Update tests for new functionality

## License

This analyzer is part of the CalTrans Bidding System and follows the same licensing terms. 