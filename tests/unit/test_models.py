"""
Unit tests for PACE data models.
"""

import pytest
from datetime import datetime
from pace.models.project import Project, ProjectType, ProjectStatus, ProjectAnalysis, QuantityItem
from pace.models.catalog import Catalog, Product, ProductCategory, ProductUnit


class TestProject:
    """Test Project model."""
    
    def test_project_creation(self, sample_project_data):
        """Test creating a new project."""
        project = Project(**sample_project_data)
        project.generate_id()
        
        assert project.name == "Test Highway Project"
        assert project.project_type == ProjectType.HIGHWAY
        assert project.agency == "CalTrans"
        assert project.status == ProjectStatus.DRAFT
        assert project.id is not None
        assert project.created_at is not None
    
    def test_project_status_properties(self):
        """Test project status properties."""
        # Active project
        active_project = Project(
            name="Active Project",
            project_type=ProjectType.HIGHWAY,
            agency="CalTrans",
            status=ProjectStatus.IN_PROGRESS
        )
        assert active_project.is_active is True
        assert active_project.is_completed is False
        
        # Completed project
        completed_project = Project(
            name="Completed Project",
            project_type=ProjectType.HIGHWAY,
            agency="CalTrans",
            status=ProjectStatus.COMPLETED
        )
        assert completed_project.is_active is False
        assert completed_project.is_completed is True
    
    def test_project_file_management(self):
        """Test project file management methods."""
        project = Project(
            name="Test Project",
            project_type=ProjectType.HIGHWAY,
            agency="CalTrans"
        )
        
        # Add specification file
        project.add_specification_file("specs.pdf")
        assert "specs.pdf" in project.specification_files
        
        # Add drawing file
        project.add_drawing_file("drawing.pdf")
        assert "drawing.pdf" in project.drawing_files
        
        # Test duplicate prevention
        project.add_specification_file("specs.pdf")
        assert project.specification_files.count("specs.pdf") == 1
    
    def test_project_tag_management(self):
        """Test project tag management."""
        project = Project(
            name="Test Project",
            project_type=ProjectType.HIGHWAY,
            agency="CalTrans"
        )
        
        project.add_tag("highway")
        project.add_tag("bridge")
        assert "highway" in project.tags
        assert "bridge" in project.tags
        
        # Test duplicate prevention
        project.add_tag("highway")
        assert project.tags.count("highway") == 1


class TestProjectAnalysis:
    """Test ProjectAnalysis model."""
    
    def test_analysis_creation(self):
        """Test creating a new project analysis."""
        analysis = ProjectAnalysis(
            project_id="test-project-id",
            total_items=5,
            total_quantity=100.0,
            confidence_score=0.85
        )
        analysis.generate_id()
        
        assert analysis.project_id == "test-project-id"
        assert analysis.total_items == 5
        assert analysis.total_quantity == 100.0
        assert analysis.confidence_score == 0.85
        assert analysis.analysis_date is not None
    
    def test_analysis_item_management(self):
        """Test adding items to analysis."""
        analysis = ProjectAnalysis(
            project_id="test-project-id",
            total_items=0,
            total_quantity=0.0,
            confidence_score=0.85
        )
        
        item1 = QuantityItem(
            item_code="ITEM-001",
            description="Test Item 1",
            unit="each",
            quantity=10.0,
            unit_price=5.0
        )
        
        item2 = QuantityItem(
            item_code="ITEM-002",
            description="Test Item 2",
            unit="linear_foot",
            quantity=50.0,
            unit_price=2.0
        )
        
        analysis.add_item(item1)
        analysis.add_item(item2)
        
        assert len(analysis.items) == 2
        assert analysis.total_items == 2
        assert analysis.total_quantity == 60.0
    
    def test_analysis_cost_calculation(self):
        """Test cost calculation in analysis."""
        analysis = ProjectAnalysis(
            project_id="test-project-id",
            total_items=0,
            total_quantity=0.0,
            confidence_score=0.85
        )
        
        item1 = QuantityItem(
            item_code="ITEM-001",
            description="Test Item 1",
            unit="each",
            quantity=10.0,
            unit_price=5.0
        )
        
        item2 = QuantityItem(
            item_code="ITEM-002",
            description="Test Item 2",
            unit="linear_foot",
            quantity=50.0,
            unit_price=2.0
        )
        
        analysis.add_item(item1)
        analysis.add_item(item2)
        
        total_cost = analysis.calculate_estimated_cost()
        expected_cost = (10.0 * 5.0) + (50.0 * 2.0)  # 50 + 100 = 150
        assert total_cost == expected_cost
        assert analysis.estimated_cost == expected_cost


class TestQuantityItem:
    """Test QuantityItem model."""
    
    def test_quantity_item_creation(self):
        """Test creating a new quantity item."""
        item = QuantityItem(
            item_code="ITEM-001",
            description="Test Item",
            unit="each",
            quantity=10.0,
            unit_price=5.0
        )
        
        assert item.item_code == "ITEM-001"
        assert item.description == "Test Item"
        assert item.unit == "each"
        assert item.quantity == 10.0
        assert item.unit_price == 5.0
    
    def test_quantity_item_total_calculation(self):
        """Test total price calculation."""
        item = QuantityItem(
            item_code="ITEM-001",
            description="Test Item",
            unit="each",
            quantity=10.0,
            unit_price=5.0
        )
        
        total = item.calculate_total()
        assert total == 50.0
        assert item.total_price == 50.0
    
    def test_quantity_item_no_price(self):
        """Test item without unit price."""
        item = QuantityItem(
            item_code="ITEM-001",
            description="Test Item",
            unit="each",
            quantity=10.0
        )
        
        total = item.calculate_total()
        assert total == 0.0
        assert item.total_price is None


class TestCatalog:
    """Test Catalog model."""
    
    def test_catalog_creation(self, sample_catalog_data):
        """Test creating a new catalog."""
        catalog = Catalog(**sample_catalog_data)
        catalog.generate_id()
        
        assert catalog.name == "Test Catalog"
        assert catalog.supplier == "Test Supplier"
        assert catalog.version == "1.0"
        assert catalog.id is not None
        assert catalog.created_at is not None
    
    def test_catalog_product_management(self, sample_product):
        """Test adding and removing products from catalog."""
        catalog = Catalog(
            name="Test Catalog",
            supplier="Test Supplier"
        )
        catalog.generate_id()
        
        # Add product
        catalog.add_product(sample_product)
        assert len(catalog.products) == 1
        assert catalog.total_products == 1
        assert sample_product.catalog_id == catalog.id
        
        # Remove product
        success = catalog.remove_product(sample_product.id)
        assert success is True
        assert len(catalog.products) == 0
        assert catalog.total_products == 0
    
    def test_catalog_search(self, sample_products):
        """Test catalog product search."""
        catalog = Catalog(
            name="Test Catalog",
            supplier="Test Supplier"
        )
        catalog.generate_id()
        
        for product in sample_products:
            catalog.add_product(product)
        
        # Search by name
        results = catalog.search_products("concrete")
        assert len(results) == 1
        assert results[0].name == "Concrete Mix"
        
        # Search by item code
        results = catalog.search_products("STEEL")
        assert len(results) == 1
        assert results[0].item_code == "STEEL-001"
    
    def test_catalog_statistics(self, sample_products):
        """Test catalog statistics calculation."""
        catalog = Catalog(
            name="Test Catalog",
            supplier="Test Supplier"
        )
        catalog.generate_id()
        
        for product in sample_products:
            catalog.add_product(product)
        
        assert catalog.total_products == 3
        assert catalog.total_value == 425.0  # 25 + 150 + 250
        assert catalog.average_product_price == pytest.approx(141.67, rel=1e-2)
    
    def test_catalog_expiry(self):
        """Test catalog expiry functionality."""
        from datetime import timedelta
        
        # Active catalog
        catalog = Catalog(
            name="Active Catalog",
            supplier="Test Supplier"
        )
        assert catalog.is_active is True
        
        # Expired catalog
        expired_catalog = Catalog(
            name="Expired Catalog",
            supplier="Test Supplier",
            expiry_date=datetime.utcnow() - timedelta(days=1)
        )
        assert expired_catalog.is_active is False


class TestProduct:
    """Test Product model."""
    
    def test_product_creation(self, sample_product_data):
        """Test creating a new product."""
        product = Product(**sample_product_data)
        product.generate_id()
        
        assert product.item_code == "TEST-001"
        assert product.name == "Test Product"
        assert product.category == ProductCategory.MATERIALS
        assert product.unit == ProductUnit.EACH
        assert product.unit_price == 10.0
        assert product.id is not None
    
    def test_product_specification_management(self):
        """Test product specification management."""
        product = Product(
            item_code="TEST-001",
            name="Test Product",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier"
        )
        
        product.add_specification("length", "10 feet")
        product.add_specification("weight", "5 pounds")
        
        assert product.specifications["length"] == "10 feet"
        assert product.specifications["weight"] == "5 pounds"
    
    def test_product_price_update(self):
        """Test product price update."""
        product = Product(
            item_code="TEST-001",
            name="Test Product",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier"
        )
        
        original_price_date = product.price_date
        product.update_price(15.0, "EUR")
        
        assert product.unit_price == 15.0
        assert product.currency == "EUR"
        assert product.price_date > original_price_date
    
    def test_product_total_price_calculation(self):
        """Test product total price calculation."""
        product = Product(
            item_code="TEST-001",
            name="Test Product",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier"
        )
        
        total = product.calculate_total_price(5.0)
        assert total == 50.0
    
    def test_product_availability(self):
        """Test product availability checks."""
        # Available product
        available_product = Product(
            item_code="TEST-001",
            name="Test Product",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier",
            in_stock=True
        )
        assert available_product.is_available is True
        
        # Out of stock product
        out_of_stock_product = Product(
            item_code="TEST-002",
            name="Test Product 2",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier",
            in_stock=False
        )
        assert out_of_stock_product.is_available is False
        
        # Product with limited stock
        limited_stock_product = Product(
            item_code="TEST-003",
            name="Test Product 3",
            category=ProductCategory.MATERIALS,
            unit=ProductUnit.EACH,
            unit_price=10.0,
            supplier="Test Supplier",
            in_stock=True,
            stock_quantity=0
        )
        assert limited_stock_product.is_available is False 