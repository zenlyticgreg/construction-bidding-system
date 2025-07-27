# CalTrans Bidding System - UI Components

This directory contains Streamlit UI components for the CalTrans Bidding System, providing a comprehensive interface for file upload, analysis display, and bid generation.

## 📁 Directory Structure

```
ui/
├── components/
│   ├── __init__.py          # Component package exports
│   ├── file_upload.py       # File upload and validation components
│   ├── analysis_display.py  # Analysis results display components
│   └── bid_generator.py     # Bid generation and configuration components
├── demo_app.py              # Demo application showcasing all components
└── README.md               # This documentation file
```

## 🚀 Quick Start

### Running the Demo App

```bash
cd ui
streamlit run demo_app.py
```

### Using Components in Your App

```python
from components.file_upload import FileUploadComponent
from components.analysis_display import AnalysisDisplayComponent
from components.bid_generator import BidGeneratorComponent

# Initialize components
uploader = FileUploadComponent()
analyzer = AnalysisDisplayComponent()
bid_generator = BidGeneratorComponent()

# Use components
file_data = uploader.render_upload_section()
analyzer.render_analysis_overview(analysis_data)
bid_result = bid_generator.render_bid_generator(analysis_data)
```

## 📄 File Upload Components (`file_upload.py`)

### Features

- **PDF File Upload**: Drag-and-drop or click-to-upload interface
- **File Validation**: Size, type, and content validation
- **Progress Tracking**: Real-time progress bars for file processing
- **Batch Upload**: Support for multiple file uploads
- **Error Handling**: Comprehensive error messages and troubleshooting tips
- **File History**: Track uploaded files with metadata

### Key Classes and Functions

#### `FileUploadComponent`

Main component for handling file uploads with validation and processing.

```python
uploader = FileUploadComponent()
file_data = uploader.render_upload_section()
```

**Methods:**
- `render_upload_section()`: Main upload interface
- `_validate_file()`: File validation logic
- `_process_file_with_progress()`: File processing with progress tracking
- `_display_error()`: Error message display
- `_display_success()`: Success message display

#### `render_batch_upload()`

Handles multiple file uploads with batch processing.

```python
batch_files = render_batch_upload()
```

#### `render_file_history()`

Displays upload history and file management.

```python
render_file_history()
```

### Configuration

- **Max File Size**: 50MB (configurable)
- **Allowed Extensions**: PDF only
- **Progress Steps**: Reading PDF → Analyzing → Extracting → Finalizing

## 🔍 Analysis Display Components (`analysis_display.py`)

### Features

- **Interactive Tables**: Filterable and searchable terminology tables
- **Visualizations**: Charts and graphs using Plotly
- **Metrics Dashboard**: Key performance indicators
- **Alert System**: Critical alerts, warnings, and information messages
- **Export Options**: Excel, PDF, and JSON export capabilities
- **Comparison Tools**: Compare multiple analyses

### Key Classes and Functions

#### `AnalysisDisplayComponent`

Main component for displaying analysis results and visualizations.

```python
analyzer = AnalysisDisplayComponent()
analyzer.render_analysis_overview(analysis_data)
```

**Methods:**
- `render_analysis_overview()`: Main analysis display interface
- `_render_key_metrics()`: Display key performance metrics
- `_render_terminology_section()`: Terminology analysis display
- `_render_quantity_extraction_section()`: Quantity extraction results
- `_render_alerts_warnings_section()`: Alert and warning display
- `_render_charts_metrics_section()`: Interactive charts and metrics

#### `render_analysis_export()`

Provides export options for analysis results.

```python
render_analysis_export(analysis_data)
```

#### `render_analysis_comparison()`

Compares multiple analyses side-by-side.

```python
render_analysis_comparison([analysis1, analysis2, analysis3])
```

### Data Structure

Expected analysis data structure:

```python
analysis_data = {
    'total_items': 25,
    'terminology_matches': 18,
    'quantities_extracted': 42,
    'confidence_score': 87.5,
    'summary': {
        'findings': [...],
        'processing_stats': {...}
    },
    'terminology': [...],
    'quantities': [...],
    'alerts': [...],
    'warnings': [...],
    'info_messages': [...]
}
```

## 💰 Bid Generator Components (`bid_generator.py`)

### Features

- **Project Information Forms**: Comprehensive project details input
- **Bid Configuration**: Markup, overhead, profit, and tax settings
- **Line Item Management**: Editable line items with pricing
- **Pricing Summary**: Real-time cost calculations and breakdowns
- **Download Options**: Excel, PDF, and JSON bid exports
- **Bid Validation**: Quality checks and validation rules
- **Template Management**: Reusable bid templates

### Key Classes and Functions

#### `BidGeneratorComponent`

Main component for bid generation and configuration.

```python
bid_generator = BidGeneratorComponent()
bid_result = bid_generator.render_bid_generator(analysis_data)
```

**Methods:**
- `render_bid_generator()`: Main bid generation interface
- `_render_project_info_form()`: Project information input
- `_render_bid_configuration()`: Bid configuration settings
- `_render_line_items_section()`: Line item management
- `_render_pricing_summary()`: Pricing calculations and display
- `_generate_bid()`: Final bid generation

#### `render_bid_history()`

Displays bid history and management.

```python
render_bid_history()
```

#### `render_bid_templates()`

Manages bid templates and configurations.

```python
render_bid_templates()
```

#### `render_bid_validation()`

Validates bid data and provides quality checks.

```python
render_bid_validation(bid_data)
```

### Configuration Options

- **Markup Percentage**: 0-100% (default: 15%)
- **Overhead Rate**: 0-50% (default: 10%)
- **Profit Margin**: 0-50% (default: 8%)
- **Contingency Rate**: 0-20% (default: 5%)
- **Tax Rate**: 0-15% (default: 8.25%)
- **Currency**: USD, EUR, GBP
- **Escalation**: Optional cost escalation factors

## 🎨 Styling and Theming

### Color Scheme

```python
color_scheme = {
    'primary': '#1f77b4',    # Blue
    'secondary': '#ff7f0e',  # Orange
    'success': '#2ca02c',    # Green
    'warning': '#d62728',    # Red
    'info': '#9467bd'        # Purple
}
```

### Icons and Emojis

Components use consistent iconography:
- 📄 File operations
- 🔍 Analysis and search
- 💰 Financial and pricing
- ⚠️ Warnings and alerts
- ✅ Success confirmations
- 📊 Charts and metrics

## 🔧 Customization

### Extending Components

To extend components, inherit from the base classes:

```python
class CustomFileUploadComponent(FileUploadComponent):
    def __init__(self):
        super().__init__()
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def _validate_file(self, uploaded_file):
        # Custom validation logic
        pass
```

### Adding New Features

1. **New Chart Types**: Add methods to `AnalysisDisplayComponent`
2. **Custom Validations**: Extend validation logic in components
3. **Additional Export Formats**: Implement new export functions
4. **Enhanced UI Elements**: Add new Streamlit widgets and layouts

## 📊 Data Flow

```
File Upload → Analysis → Bid Generation → Export
     ↓           ↓           ↓           ↓
Validation → Display → Configuration → Download
```

## 🧪 Testing

### Running Tests

```bash
# Test individual components
python -m pytest tests/test_file_upload.py
python -m pytest tests/test_analysis_display.py
python -m pytest tests/test_bid_generator.py
```

### Test Data

Sample data structures are provided in the demo app for testing:

```python
# Sample analysis data
analysis_data = create_sample_analysis_data()

# Sample bid data
bid_data = {
    'project_info': {...},
    'bid_config': {...},
    'line_items': [...],
    'pricing_summary': {...}
}
```

## 🚀 Performance Considerations

### Optimization Tips

1. **Lazy Loading**: Load components only when needed
2. **Caching**: Use Streamlit caching for expensive operations
3. **Batch Processing**: Process multiple files efficiently
4. **Memory Management**: Clear session state when appropriate

### Memory Usage

- **File Upload**: ~50MB max per file
- **Analysis Display**: Depends on data size
- **Bid Generator**: Minimal memory footprint

## 🔒 Security

### File Upload Security

- File type validation
- Size limits
- Content verification
- Secure file handling

### Data Protection

- Session state management
- Secure data transmission
- Input validation and sanitization

## 📝 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 standards
2. **Documentation**: Add docstrings to all functions
3. **Testing**: Write tests for new features
4. **Type Hints**: Use type annotations

### Adding New Components

1. Create new component file in `components/`
2. Add imports to `__init__.py`
3. Update documentation
4. Add tests
5. Update demo app

## 📞 Support

For issues and questions:

1. Check the demo app for usage examples
2. Review component documentation
3. Examine test files for implementation details
4. Create an issue with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 