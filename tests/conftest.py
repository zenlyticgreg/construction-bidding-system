"""
Pytest configuration and fixtures for PACE tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any

from pace.core.config import Settings
from pace.models.project import Project, ProjectType, ProjectStatus
from pace.models.catalog import Catalog, Product, ProductCategory, ProductUnit
from pace.services.project_service import ProjectService


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings with temporary directories."""
    # Override settings for testing
    settings = Settings(
        data_dir=temp_dir / "data",
        logs_dir=temp_dir / "logs",
        environment="testing",
        debug=True,
    )
    return settings


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Sample project data for testing."""
    return {
        "name": "Test Highway Project",
        "project_type": ProjectType.HIGHWAY,
        "agency": "CalTrans",
        "description": "Test highway construction project",
        "location": "California",
        "budget": 1000000.0,
    }


@pytest.fixture
def sample_project(sample_project_data: Dict[str, Any]) -> Project:
    """Create a sample project for testing."""
    project = Project(**sample_project_data)
    project.generate_id()
    return project


@pytest.fixture
def sample_catalog_data() -> Dict[str, Any]:
    """Sample catalog data for testing."""
    return {
        "name": "Test Catalog",
        "description": "Test product catalog",
        "supplier": "Test Supplier",
        "version": "1.0",
    }


@pytest.fixture
def sample_catalog(sample_catalog_data: Dict[str, Any]) -> Catalog:
    """Create a sample catalog for testing."""
    catalog = Catalog(**sample_catalog_data)
    catalog.generate_id()
    return catalog


@pytest.fixture
def sample_product_data() -> Dict[str, Any]:
    """Sample product data for testing."""
    return {
        "item_code": "TEST-001",
        "name": "Test Product",
        "description": "Test product description",
        "category": ProductCategory.MATERIALS,
        "unit": ProductUnit.EACH,
        "unit_price": 10.0,
        "supplier": "Test Supplier",
    }


@pytest.fixture
def sample_product(sample_product_data: Dict[str, Any]) -> Product:
    """Create a sample product for testing."""
    product = Product(**sample_product_data)
    product.generate_id()
    return product


@pytest.fixture
def project_service(test_settings: Settings) -> ProjectService:
    """Create a project service instance for testing."""
    return ProjectService()


@pytest.fixture
def sample_projects() -> list[Project]:
    """Create multiple sample projects for testing."""
    projects = []
    
    project_data = [
        {
            "name": "Highway Bridge Project",
            "project_type": ProjectType.BRIDGE,
            "agency": "CalTrans",
            "status": ProjectStatus.IN_REVIEW,
        },
        {
            "name": "Municipal Water Treatment",
            "project_type": ProjectType.MUNICIPAL,
            "agency": "City of Sacramento",
            "status": ProjectStatus.APPROVED,
        },
        {
            "name": "Federal Courthouse",
            "project_type": ProjectType.FEDERAL,
            "agency": "GSA",
            "status": ProjectStatus.DRAFT,
        },
    ]
    
    for data in project_data:
        project = Project(**data)
        project.generate_id()
        projects.append(project)
    
    return projects


@pytest.fixture
def sample_products() -> list[Product]:
    """Create multiple sample products for testing."""
    products = []
    
    product_data = [
        {
            "item_code": "CONC-001",
            "name": "Concrete Mix",
            "category": ProductCategory.MATERIALS,
            "unit": ProductUnit.CUBIC_FOOT,
            "unit_price": 25.0,
            "supplier": "Concrete Co",
        },
        {
            "item_code": "STEEL-001",
            "name": "Steel Beam",
            "category": ProductCategory.MATERIALS,
            "unit": ProductUnit.LINEAR_FOOT,
            "unit_price": 150.0,
            "supplier": "Steel Supply",
        },
        {
            "item_code": "TOOL-001",
            "name": "Hammer Drill",
            "category": ProductCategory.TOOLS,
            "unit": ProductUnit.EACH,
            "unit_price": 250.0,
            "supplier": "Tool World",
        },
    ]
    
    for data in product_data:
        product = Product(**data)
        product.generate_id()
        products.append(product)
    
    return products 