# Caltrans Bidding System

A comprehensive bidding system for Caltrans construction projects that automates the process of analyzing project specifications, matching products, and generating competitive bids.

## Features

- **Project Analysis**: Automated analysis of Caltrans project specifications
- **Product Matching**: Intelligent matching of products to project requirements
- **Bid Generation**: Automated bid creation with competitive pricing
- **Data Extraction**: Integration with Whitecap for product data extraction
- **Reporting**: Comprehensive reporting and analytics

## Project Structure

```
caltrans-bidding-system/
├── config/                 # Configuration files
│   ├── catalog_sections.json
│   └── settings.py
├── data/                   # Reference data
│   └── caltrans_reference.json
├── examples/               # Example usage
│   └── bid_engine_example.py
├── output/                 # Generated outputs
│   ├── bids/
│   ├── catalogs/
│   └── reports/
├── src/                    # Source code
│   ├── analyzers/          # Analysis modules
│   ├── bidding/            # Bidding engine
│   ├── extractors/         # Data extraction
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── ui/                     # User interface components
└── requirements.txt        # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zenlyticgreg/construction-bidding-system.git
cd caltrans-bidding-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.bidding.bid_engine import BidEngine
from src.analyzers.caltrans_analyzer import CaltransAnalyzer

# Initialize components
analyzer = CaltransAnalyzer()
bid_engine = BidEngine()

# Analyze project
project_data = analyzer.analyze_project("project_specs.pdf")

# Generate bid
bid = bid_engine.generate_bid(project_data)
```

### Example

See `examples/bid_engine_example.py` for a complete usage example.

## Configuration

Update `config/settings.py` to configure:
- API endpoints
- Database connections
- Output directories
- Pricing parameters

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team. 