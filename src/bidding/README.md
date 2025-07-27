# CalTrans Bidding Engine

The CalTrans Bidding Engine is a comprehensive system that combines CalTrans PDF analysis with Whitecap product matching to generate complete bid packages with line items, pricing calculations, and project-specific configurations.

## Features

### Core Functionality
- **PDF Analysis Integration**: Combines CalTrans analysis with product matching
- **Complete Bid Generation**: Creates full bid packages with line items
- **Smart Pricing**: Applies markup, delivery fees, and waste factors
- **Quantity Calculation**: Determines quantities based on CalTrans terminology
- **Product Matching**: Intelligent matching between CalTrans terms and Whitecap products
- **Bid Summary**: Provides comprehensive pricing breakdown

### Pricing Logic
- **Default Markup**: 20% (configurable)
- **Delivery Fee**: 3% or $150 minimum
- **Waste Factors**:
  - Formwork: 10%
  - Lumber: 10%
  - Hardware: 5%
  - Specialty: 15%
  - Default: 8%

### Product Matching Strategies
The engine uses intelligent matching strategies for different CalTrans terms:

| CalTrans Term | Search Keywords |
|---------------|-----------------|
| BALUSTER | concrete, form, heavy, plywood, CDX |
| BLOCKOUT | lumber, 2x4, 2x6, construction, grade |
| STAMPED CONCRETE | texture, form, liner, pattern |
| RETAINING WALL | form, tie, plywood, wall |
| EROSION CONTROL | post, stake, treated, fence |
| FORMWORK | plywood, form, CDX, sheathing |
| FALSEWORK | lumber, support, temporary, structure |
| BRIDGE RAILING | steel, rail, post, hardware |
| CONCRETE FINISHING | tool, finish, texture, pattern |
| TEMPORARY STRUCTURES | lumber, plywood, hardware, support |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure the project structure is set up
mkdir -p output/bids
mkdir -p output/catalogs
mkdir -p output/reports
```

## Usage

### Basic Usage

```python
from bidding.bid_engine import CalTransBiddingEngine

# Create the bidding engine
engine = CalTransBiddingEngine()

# Generate a complete bid
bid_data = engine.generate_complete_bid(
    pdf_path="path/to/caltrans_project.pdf",
    project_name="Bridge Railing Replacement",
    project_number="CA-2024-001",
    markup_percentage=0.20  # 20% markup
)

# Save the bid to file
engine.save_bid_to_file(bid_data, "output/bids/bid_package.json")
```

### Advanced Usage

```python
from bidding.bid_engine import CalTransBiddingEngine, BidLineItem

# Create engine
engine = CalTransBiddingEngine()

# Find products for specific terms
term_data = {"term": "BALUSTER", "category": "bridge_barrier"}
products = engine.find_products_for_term(term_data)

# Calculate quantities needed
from analyzers.caltrans_analyzer import ExtractedQuantity
quantities = [
    ExtractedQuantity(value=100.0, unit="EA", context="baluster", page_number=1)
]
quantity_needed = engine.calculate_quantity_needed(term_data, quantities)

# Calculate pricing summary
line_items = [
    BidLineItem(
        item_number="001",
        description="BALUSTER - bridge_barrier",
        caltrans_term="BALUSTER",
        quantity=100.0,
        unit="EA",
        unit_price=25.0,
        total_price=2500.0
    )
]
pricing = engine.calculate_pricing_summary(line_items)
```

## Data Structures

### BidLineItem
Represents a single line item in a bid:

```python
@dataclass
class BidLineItem:
    item_number: str
    description: str
    caltrans_term: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    product_matches: List[Dict[str, Any]]
    waste_factor: float = 0.08
    markup_percentage: float = 0.20
    delivery_fee: float = 0.0
    notes: str = ""
    confidence: float = 1.0
```

### PricingSummary
Contains the complete pricing breakdown:

```python
@dataclass
class PricingSummary:
    subtotal: float
    markup_amount: float
    delivery_fee: float
    waste_adjustments: float
    total: float
    line_item_count: int
    high_priority_items: int
    estimated_materials_cost: float
    estimated_labor_cost: float
```

### BidPackage
Complete bid package with all components:

```python
@dataclass
class BidPackage:
    project_name: str
    project_number: str
    bid_date: datetime
    line_items: List[BidLineItem]
    pricing_summary: PricingSummary
    analysis_results: Optional[CalTransAnalysisResult]
    markup_percentage: float
    delivery_fee: float
    notes: str
    metadata: Dict[str, Any]
```

## Configuration

### Pricing Configuration
The engine uses a `PricingConfig` class for pricing settings:

```python
class PricingConfig:
    DEFAULT_MARKUP = 0.20  # 20%
    DELIVERY_PERCENTAGE = 0.03  # 3%
    DELIVERY_MINIMUM = 150.00  # $150 minimum
    WASTE_FACTORS = {
        "formwork": 0.10,
        "lumber": 0.10,
        "hardware": 0.05,
        "specialty": 0.15,
        "default": 0.08
    }
```

### Waste Factors
Different material categories have different waste factors:

- **Formwork**: 10% (plywood, forms, sheathing)
- **Lumber**: 10% (dimensional lumber, 2x4, 2x6, etc.)
- **Hardware**: 5% (bolts, screws, nails, fasteners)
- **Specialty**: 15% (custom items, special materials)
- **Default**: 8% (general materials)

## Output Format

The bid engine generates JSON output with the following structure:

```json
{
  "project_name": "Bridge Railing Replacement",
  "project_number": "CA-2024-001",
  "bid_date": "2024-01-15T10:30:00",
  "markup_percentage": 0.20,
  "delivery_fee": 150.00,
  "line_items": [
    {
      "item_number": "001",
      "description": "BALUSTER - bridge_barrier",
      "caltrans_term": "BALUSTER",
      "quantity": 100.0,
      "unit": "EA",
      "unit_price": 25.0,
      "total_price": 2500.0,
      "waste_factor": 0.10,
      "markup_percentage": 0.20,
      "product_matches": [...],
      "notes": "Page 1: baluster installation..."
    }
  ],
  "pricing_summary": {
    "subtotal": 2500.0,
    "markup_amount": 500.0,
    "delivery_fee": 150.0,
    "waste_adjustments": 250.0,
    "total": 3400.0,
    "line_item_count": 1,
    "high_priority_items": 1,
    "estimated_materials_cost": 1750.0,
    "estimated_labor_cost": 750.0
  },
  "analysis_metadata": {
    "total_terms_found": 5,
    "total_quantities": 3,
    "high_priority_terms": 2,
    "critical_alerts": 0
  }
}
```

## Error Handling

The bidding engine includes comprehensive error handling:

- **File Not Found**: Handles missing PDF files gracefully
- **Analysis Errors**: Logs and continues processing when analysis fails
- **Product Matching**: Falls back to estimated pricing when no matches found
- **Quantity Calculation**: Uses default values when quantities can't be determined
- **Pricing Errors**: Provides fallback calculations for edge cases

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/test_bid_engine.py -v

# Run specific test
python -m pytest tests/test_bid_engine.py::TestCalTransBiddingEngine::test_initialization -v
```

## Examples

See `examples/bid_engine_example.py` for comprehensive usage examples including:

- Basic bid generation
- Product matching demonstration
- Quantity calculation examples
- Pricing calculation examples

## Dependencies

The bidding engine depends on:

- `analyzers.caltrans_analyzer`: For PDF analysis
- `analyzers.product_matcher`: For product matching
- `config.settings`: For configuration management
- `utils.data_validator`: For data validation

## Contributing

When contributing to the bidding engine:

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any new features
4. Ensure error handling is robust
5. Maintain backward compatibility

## License

This module is part of the CalTrans Bidding System and follows the same licensing terms as the main project. 