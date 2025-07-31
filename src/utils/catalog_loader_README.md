# Catalog Loader Utility

This module provides functionality to load and manage sample product catalogs for the PACE construction estimating system.

## Features

- **Sample Catalog Loading**: Load pre-generated sample construction catalogs
- **Catalog Summary Display**: Generate and display catalog statistics
- **Data Conversion**: Convert between different data formats
- **Search and Filter**: Search and filter catalog data by various criteria

## Functions

### `load_sample_catalog()`
Loads the sample catalog from `pace_sample_catalog.json` or `pace_sample_catalog.csv`.

**Returns:**
- List of product dictionaries with fields: `category`, `name`, `price`, `sku`, `unit`, `item_num`

### `display_catalog_summary(catalog_data)`
Displays comprehensive catalog statistics including:
- Total number of products
- Number of categories
- Average price
- Category breakdown table

### `convert_catalog_to_dataframe(catalog_data)`
Converts catalog data to pandas DataFrame for easier manipulation.

### `get_catalog_categories(catalog_data)`
Returns a list of unique categories in the catalog.

### `filter_catalog_by_category(catalog_data, category)`
Filters catalog data by a specific category.

### `search_catalog(catalog_data, search_term)`
Searches catalog data by name, SKU, or item number.

## Usage in PACE Application

The catalog loader is integrated into the main PACE application in two locations:

### 1. Dashboard
- Quick access to load sample catalog
- View catalog summary
- Navigate to catalog section

### 2. Extract Catalog Page
- Load sample catalog for testing
- View detailed catalog summary
- Display catalog status

## Sample Catalog Structure

The sample catalog contains 104 construction products across 17 categories:

- **Concrete**: Ready-mix, fiber reinforced, admixtures
- **Masonry**: Concrete blocks, bricks, mortar
- **Metals**: Rebar, structural steel, fasteners
- **Wood**: Lumber, plywood, engineered wood
- **Roofing**: Shingles, membranes, insulation
- **Electrical**: Conduit, wire, fixtures
- **Plumbing**: Pipes, fittings, fixtures
- **HVAC**: Ductwork, equipment, controls
- **Finishes**: Paint, flooring, ceiling tiles
- **Site Work**: Excavation, grading, paving
- **Landscaping**: Plants, irrigation, hardscape
- **Safety**: Barriers, signage, PPE
- **Tools**: Hand tools, power tools, equipment
- **Supplies**: Adhesives, sealants, hardware
- **Specialty**: Custom items, specialty materials
- **Services**: Labor, delivery, installation

## Integration

The catalog loader is automatically imported in `main.py` and provides:

1. **Session State Management**: Stores catalog data in `st.session_state.catalog_data`
2. **System Status Updates**: Updates `st.session_state.system_status['catalog_loaded']`
3. **User Feedback**: Provides success/error messages and loading indicators
4. **Data Validation**: Handles missing files and invalid data formats gracefully

## Error Handling

The module includes comprehensive error handling for:
- Missing catalog files
- Invalid JSON/CSV formats
- Missing required fields
- File permission issues
- Data corruption

## Performance

- **Loading Time**: < 1 second for 100+ products
- **Memory Usage**: Minimal overhead
- **Scalability**: Supports catalogs with thousands of products 