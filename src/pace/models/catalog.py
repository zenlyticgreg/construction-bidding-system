"""
Catalog-related data models for PACE application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from .base import TimestampedModel, IdentifiableModel, Field


class ProductCategory(str, Enum):
    """Product categories."""
    MATERIALS = "materials"
    EQUIPMENT = "equipment"
    TOOLS = "tools"
    SUPPLIES = "supplies"
    SAFETY = "safety"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    OTHER = "other"


class ProductUnit(str, Enum):
    """Product units of measurement."""
    EACH = "each"
    LINEAR_FOOT = "linear_foot"
    SQUARE_FOOT = "square_foot"
    CUBIC_FOOT = "cubic_foot"
    POUND = "pound"
    TON = "ton"
    GALLON = "gallon"
    LITER = "liter"
    METER = "meter"
    YARD = "yard"
    BUNDLE = "bundle"
    CASE = "case"
    PACK = "pack"
    ROLL = "roll"
    SHEET = "sheet"


class Product(TimestampedModel, IdentifiableModel):
    """Model for catalog products."""
    
    catalog_id: str = Field(description="Associated catalog ID")
    item_code: str = Field(description="Product item code")
    name: str = Field(description="Product name")
    description: Optional[str] = Field(default=None, description="Product description")
    category: ProductCategory = Field(description="Product category")
    unit: ProductUnit = Field(description="Unit of measurement")
    
    # Pricing
    unit_price: float = Field(description="Unit price")
    currency: str = Field(default="USD", description="Currency code")
    price_date: datetime = Field(default_factory=datetime.utcnow, description="Price date")
    
    # Specifications
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Product specifications")
    dimensions: Optional[Dict[str, float]] = Field(default=None, description="Product dimensions")
    weight: Optional[float] = Field(default=None, description="Product weight")
    
    # Availability
    in_stock: bool = Field(default=True, description="In stock status")
    stock_quantity: Optional[float] = Field(default=None, description="Available quantity")
    lead_time_days: Optional[int] = Field(default=None, description="Lead time in days")
    
    # Supplier information
    supplier: str = Field(description="Supplier name")
    supplier_code: Optional[str] = Field(default=None, description="Supplier product code")
    manufacturer: Optional[str] = Field(default=None, description="Manufacturer name")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Product tags")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    def add_specification(self, key: str, value: Any) -> None:
        """Add a specification to the product."""
        self.specifications[key] = value
        self.update_timestamp()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the product."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    def update_price(self, new_price: float, currency: str = "USD") -> None:
        """Update the product price."""
        self.unit_price = new_price
        self.currency = currency
        self.price_date = datetime.utcnow()
        self.update_timestamp()
    
    def calculate_total_price(self, quantity: float) -> float:
        """Calculate total price for a given quantity."""
        return self.unit_price * quantity
    
    @property
    def is_available(self) -> bool:
        """Check if product is available."""
        return self.in_stock and (self.stock_quantity is None or self.stock_quantity > 0)


class ProductCategory(TimestampedModel, IdentifiableModel):
    """Model for product categories."""
    
    name: str = Field(description="Category name")
    description: Optional[str] = Field(default=None, description="Category description")
    parent_category_id: Optional[str] = Field(default=None, description="Parent category ID")
    
    # Category metadata
    icon: Optional[str] = Field(default=None, description="Category icon")
    color: Optional[str] = Field(default=None, description="Category color")
    sort_order: int = Field(default=0, description="Sort order")
    
    # Statistics
    product_count: int = Field(default=0, description="Number of products in category")
    
    def increment_product_count(self) -> None:
        """Increment the product count."""
        self.product_count += 1
        self.update_timestamp()
    
    def decrement_product_count(self) -> None:
        """Decrement the product count."""
        if self.product_count > 0:
            self.product_count -= 1
            self.update_timestamp()


class Catalog(TimestampedModel, IdentifiableModel):
    """Model for product catalogs."""
    
    name: str = Field(description="Catalog name")
    description: Optional[str] = Field(default=None, description="Catalog description")
    supplier: str = Field(description="Supplier name")
    
    # Catalog details
    version: str = Field(default="1.0", description="Catalog version")
    effective_date: datetime = Field(default_factory=datetime.utcnow, description="Effective date")
    expiry_date: Optional[datetime] = Field(default=None, description="Expiry date")
    
    # File information
    source_file: Optional[str] = Field(default=None, description="Source file path")
    file_format: Optional[str] = Field(default=None, description="File format")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    
    # Content
    products: List[Product] = Field(default_factory=list, description="Catalog products")
    categories: List[ProductCategory] = Field(default_factory=list, description="Product categories")
    
    # Statistics
    total_products: int = Field(default=0, description="Total number of products")
    total_value: float = Field(default=0.0, description="Total catalog value")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Catalog tags")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    def add_product(self, product: Product) -> None:
        """Add a product to the catalog."""
        product.catalog_id = self.id
        self.products.append(product)
        self.total_products = len(self.products)
        self.total_value += product.unit_price
        self.update_timestamp()
    
    def remove_product(self, product_id: str) -> bool:
        """Remove a product from the catalog."""
        for i, product in enumerate(self.products):
            if product.id == product_id:
                removed_product = self.products.pop(i)
                self.total_products = len(self.products)
                self.total_value -= removed_product.unit_price
                self.update_timestamp()
                return True
        return False
    
    def get_products_by_category(self, category: ProductCategory) -> List[Product]:
        """Get products by category."""
        return [p for p in self.products if p.category == category]
    
    def get_products_by_supplier(self, supplier: str) -> List[Product]:
        """Get products by supplier."""
        return [p for p in self.products if p.supplier.lower() == supplier.lower()]
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name, description, or item code."""
        query = query.lower()
        results = []
        
        for product in self.products:
            if (query in product.name.lower() or
                (product.description and query in product.description.lower()) or
                query in product.item_code.lower()):
                results.append(product)
        
        return results
    
    def add_category(self, category: ProductCategory) -> None:
        """Add a category to the catalog."""
        self.categories.append(category)
        self.update_timestamp()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the catalog."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    @property
    def is_active(self) -> bool:
        """Check if catalog is active (not expired)."""
        if self.expiry_date is None:
            return True
        return datetime.utcnow() < self.expiry_date
    
    @property
    def average_product_price(self) -> float:
        """Calculate average product price."""
        if not self.products:
            return 0.0
        return self.total_value / len(self.products) 