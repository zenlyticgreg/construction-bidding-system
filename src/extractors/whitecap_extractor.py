"""
Whitecap Catalog Extractor for PACE - Project Analysis & Construction Estimating

This module provides functionality to extract product information from Whitecap
catalog PDFs for use in the PACE construction bidding automation platform.

The extractor supports:
- PDF text extraction and parsing
- Table data extraction
- Product information identification
- Pricing and specification extraction
- Multi-format export capabilities

For more information, visit: https://pace-construction.com
"""

import os
import sys
import json
import logging
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import (
    Dict, List, Tuple, Optional, Union, Any, Set,
    Generator, NamedTuple
)
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Third-party imports
import pdfplumber
from pdfplumber.table import Table
import pandas as pd

# Local imports
from src.utils.data_validator import DataValidator, ValidationResult, ProgressTracker
from config.settings import get_setting


class ProductCategory(Enum):
    """Product categories for Whitecap catalog"""
    FORMWORK = "formwork"
    LUMBER = "lumber"
    HARDWARE = "hardware"
    DRAINAGE = "drainage"
    SAFETY = "safety"
    TOOLS = "tools"
    CONCRETE = "concrete"
    MASONRY = "masonry"
    DECORATIVE = "decorative"
    GEOSYNTHETICS = "geosynthetics"
    UNKNOWN = "unknown"


class ExtractionPriority(Enum):
    """Extraction priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class ProductData:
    """Standardized product data structure"""
    sku: str
    product_name: str
    description: str
    size: str
    unit: str
    price: Optional[float] = None
    category: ProductCategory = ProductCategory.UNKNOWN
    priority: ExtractionPriority = ExtractionPriority.LOW
    page_number: Optional[int] = None
    section: Optional[str] = None
    construction_relevance: str = "low"
    extracted_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0


@dataclass
class ExtractionConfig:
    """Configuration for catalog extraction"""
    start_page: int = 1
    end_page: int = 868
    priority_sections: List[str] = field(default_factory=lambda: [
        "concrete_forming", "fastening_systems", "decorative_concrete"
    ])
    table_headers: List[str] = field(default_factory=lambda: [
        "PRODUCT NO.", "SKU", "SIZE", "DESCRIPTION", "PRICE"
    ])
    min_confidence_score: float = 0.7
    enable_progress_tracking: bool = True
    enable_validation: bool = True
    export_format: str = "csv"


class WhitecapCatalogExtractor:
    """Main extractor class for Whitecap catalog processing"""
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize the Whitecap catalog extractor"""
        self.config = config or ExtractionConfig()
        self.logger = self._setup_logger()
        self.validator = DataValidator()
        self.settings = get_setting('WHITECAP_EXTRACTOR_CONFIG', {})  # Fix: provide key parameter
        
        # Load catalog sections configuration
        self.catalog_sections = self._load_catalog_sections()
        
        # Product extraction patterns
        self.table_patterns = self._setup_table_patterns()
        self.text_patterns = self._setup_text_patterns()
        
        # Category keywords
        self.category_keywords = self._setup_category_keywords()
        
        # Extraction statistics
        self.stats = {
            "total_pages": 0,
            "processed_pages": 0,
            "extracted_products": 0,
            "table_products": 0,
            "text_products": 0,
            "errors": 0,
            "warnings": 0
        }
        
        # Progress tracker
        self.progress_tracker: Optional[ProgressTracker] = None
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for extraction operations"""
        logger = logging.getLogger("whitecap_extractor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_catalog_sections(self) -> Dict[str, Any]:
        """Load catalog sections configuration"""
        try:
            sections_path = Path("config/catalog_sections.json")
            if sections_path.exists():
                with open(sections_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning("Catalog sections configuration not found")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading catalog sections: {e}")
            return {}
    
    def _setup_table_patterns(self) -> Dict[str, re.Pattern]:
        """Setup regex patterns for table extraction"""
        return {
            "sku_pattern": re.compile(r'^[A-Z0-9\-\.]+$', re.IGNORECASE),
            "price_pattern": re.compile(r'^\$?[\d,]+\.?\d*$'),
            "size_pattern": re.compile(r'[\d\.]+[x×][\d\.]+|[\d\.]+\s*(?:ft|in|cm|mm|yd|m)', re.IGNORECASE),
            "product_no_pattern": re.compile(r'^[A-Z0-9\-\.]+$', re.IGNORECASE),
            "description_pattern": re.compile(r'[A-Za-z\s\-\(\)]+', re.IGNORECASE)
        }
    
    def _setup_text_patterns(self) -> Dict[str, re.Pattern]:
        """Setup regex patterns for text extraction"""
        return {
            "product_line": re.compile(
                r'([A-Z0-9\-\.]+)\s+([^$]+?)\s+(\$?[\d,]+\.?\d*)',
                re.IGNORECASE
            ),
            "sku_description": re.compile(
                r'([A-Z0-9\-\.]+)\s+([^$]+?)(?:\s+(\$?[\d,]+\.?\d*))?',
                re.IGNORECASE
            ),
            "size_extraction": re.compile(
                r'(\d+(?:\.\d+)?)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*(ft|in|cm|mm|yd|m)',
                re.IGNORECASE
            )
        }
    
    def _setup_category_keywords(self) -> Dict[ProductCategory, Set[str]]:
        """Setup keywords for product categorization"""
        return {
            ProductCategory.FORMWORK: {
                "form", "forming", "formwork", "shoring", "falsework", "waling",
                "tie", "panel", "liner", "release", "edge", "column", "deck"
            },
            ProductCategory.LUMBER: {
                "lumber", "wood", "plywood", "osb", "2x4", "2x6", "2x8", "2x10",
                "4x4", "4x6", "6x6", "timber", "beam", "post"
            },
            ProductCategory.HARDWARE: {
                "nail", "screw", "bolt", "anchor", "connector", "hanger",
                "bracket", "clip", "fastener", "tie", "wire"
            },
            ProductCategory.DRAINAGE: {
                "drain", "pipe", "basin", "fitting", "fabric", "geotextile",
                "erosion", "retention", "drainage"
            },
            ProductCategory.SAFETY: {
                "safety", "hard hat", "gloves", "vest", "glasses", "boots",
                "protection", "ppe", "fall", "respiratory"
            },
            ProductCategory.TOOLS: {
                "tool", "drill", "saw", "hammer", "wrench", "screwdriver",
                "level", "tape", "measure", "laser"
            },
            ProductCategory.CONCRETE: {
                "concrete", "cement", "aggregate", "admixture", "rebar",
                "wire mesh", "fiber", "mix", "cure"
            },
            ProductCategory.MASONRY: {
                "brick", "mortar", "grout", "masonry", "trowel", "pointing"
            },
            ProductCategory.DECORATIVE: {
                "stamp", "stain", "overlay", "texture", "color", "sealer",
                "decorative", "polish"
            },
            ProductCategory.GEOSYNTHETICS: {
                "geosynthetic", "geotextile", "geogrid", "geocomposite"
            }
        }
    
    def extract_catalog_data(self, pdf_path: Union[str, Path]) -> pd.DataFrame:
        """
        Extract all product data from Whitecap catalog PDF
        
        Args:
            pdf_path: Path to the Whitecap catalog PDF
            
        Returns:
            DataFrame with standardized product information
        """
        pdf_path = Path(pdf_path)
        
        # Validate PDF file
        validation_result = self.validator.validate_pdf_upload(pdf_path)
        if not validation_result.is_valid:
            self.logger.error(f"PDF validation failed: {validation_result.message}")
            raise ValueError(f"Invalid PDF file: {validation_result.message}")
        
        self.logger.info(f"Starting catalog extraction from {pdf_path}")
        
        # Initialize progress tracker
        if self.config.enable_progress_tracking:
            self.progress_tracker = self.validator.create_progress_tracker(
                self.config.end_page - self.config.start_page + 1
            )
        
        # Extract data by sections
        all_products = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.stats["total_pages"] = len(pdf.pages)
                
                for page_num in range(self.config.start_page - 1, min(self.config.end_page, len(pdf.pages))):
                    try:
                        page = pdf.pages[page_num]
                        page_products = self.process_page(page, page_num + 1)
                        all_products.extend(page_products)
                        
                        # Update progress
                        if self.progress_tracker:
                            self.progress_tracker.update(
                                f"page_{page_num + 1}",
                                success=True,
                                message=f"Extracted {len(page_products)} products"
                            )
                        
                        self.stats["processed_pages"] += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error processing page {page_num + 1}: {e}")
                        self.stats["errors"] += 1
                        
                        if self.progress_tracker:
                            self.progress_tracker.update(
                                f"page_{page_num + 1}",
                                success=False,
                                message=str(e)
                            )
        
        except Exception as e:
            self.logger.error(f"Error opening PDF: {e}")
            raise
        
        # Convert to DataFrame
        df = pd.DataFrame([product.__dict__ for product in all_products])
        
        # Clean and standardize data
        df = self.clean_dataframe(df)
        
        # Update statistics
        self.stats["extracted_products"] = len(df)
        
        self.logger.info(f"Extraction completed: {len(df)} products from {self.stats['processed_pages']} pages")
        
        return df
    
    def extract_by_sections(
        self, 
        pdf_path: Union[str, Path], 
        sections_config: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Extract data from specific catalog sections
        
        Args:
            pdf_path: Path to the Whitecap catalog PDF
            sections_config: Configuration for section extraction
            
        Returns:
            DataFrame with products from specified sections
        """
        pdf_path = Path(pdf_path)
        
        # Validate PDF file
        validation_result = self.validator.validate_pdf_upload(pdf_path)
        if not validation_result.is_valid:
            self.logger.error(f"PDF validation failed: {validation_result.message}")
            raise ValueError(f"Invalid PDF file: {validation_result.message}")
        
        self.logger.info(f"Starting section-based extraction from {pdf_path}")
        
        all_products = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for section_name, section_config in sections_config.items():
                    if section_name not in self.catalog_sections.get("catalog_sections", {}):
                        self.logger.warning(f"Unknown section: {section_name}")
                        continue
                    
                    section_data = self.catalog_sections["catalog_sections"][section_name]
                    start_page = section_data["page_range"]["start"]
                    end_page = section_data["page_range"]["end"]
                    
                    self.logger.info(f"Processing section {section_name}: pages {start_page}-{end_page}")
                    
                    for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                        try:
                            page = pdf.pages[page_num]
                            page_products = self.process_page(page, page_num + 1, section_name)
                            
                            # Add section information
                            for product in page_products:
                                product.section = section_name
                            
                            all_products.extend(page_products)
                            
                        except Exception as e:
                            self.logger.error(f"Error processing page {page_num + 1} in section {section_name}: {e}")
                            self.stats["errors"] += 1
        
        except Exception as e:
            self.logger.error(f"Error in section extraction: {e}")
            raise
        
        # Convert to DataFrame
        df = pd.DataFrame([product.__dict__ for product in all_products])
        
        # Clean and standardize data
        df = self.clean_dataframe(df)
        
        self.logger.info(f"Section extraction completed: {len(df)} products")
        
        return df
    
    def process_page(
        self, 
        page, 
        page_num: int, 
        section: Optional[str] = None
    ) -> List[ProductData]:
        """
        Process a single page and extract products
        
        Args:
            page: PDF page object
            page_num: Page number
            section: Section name (optional)
            
        Returns:
            List of extracted products
        """
        products = []
        
        try:
            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:  # At least header and one data row
                    table_products = self.extract_products_from_table(table, page_num)
                    products.extend(table_products)
                    self.stats["table_products"] += len(table_products)
            
            # Extract text-based products
            text = page.extract_text()
            if text:
                text_products = self.extract_products_from_text(text, page_num)
                products.extend(text_products)
                self.stats["text_products"] += len(text_products)
            
            # Add section information
            if section:
                for product in products:
                    product.section = section
            
        except Exception as e:
            self.logger.error(f"Error processing page {page_num}: {e}")
            self.stats["errors"] += 1
        
        return products
    
    def extract_products_from_table(
        self, 
        table: List[List[str]], 
        page_num: int
    ) -> List[ProductData]:
        """
        Extract products from a table structure
        
        Args:
            table: Table data as list of lists
            page_num: Page number
            
        Returns:
            List of extracted products
        """
        products = []
        
        if not table or len(table) < 2:
            return products
        
        # Identify header row
        header_row = None
        for i, row in enumerate(table):
            if row and any(any(header in str(cell).upper() for header in self.config.table_headers) for cell in row if cell):
                header_row = i
                break
        
        if header_row is None:
            return products
        
        # Map column indices
        headers = [str(cell).upper().strip() if cell else "" for cell in table[header_row]]
        column_map = {}
        
        for i, header in enumerate(headers):
            if "PRODUCT" in header or "SKU" in header or "NO" in header:
                column_map["sku"] = i
            elif "SIZE" in header or "DIMENSION" in header:
                column_map["size"] = i
            elif "DESCRIPTION" in header or "NAME" in header:
                column_map["description"] = i
            elif "PRICE" in header or "$" in header:
                column_map["price"] = i
        
        # Extract products from data rows
        for row_idx in range(header_row + 1, len(table)):
            row = table[row_idx]
            if not row or all(not cell for cell in row):
                continue
            
            try:
                product = self._create_product_from_row(row, column_map, page_num)
                if product:
                    products.append(product)
            
            except Exception as e:
                self.logger.warning(f"Error extracting product from table row {row_idx}: {e}")
                self.stats["warnings"] += 1
        
        return products
    
    def extract_products_from_text(
        self, 
        text: str, 
        page_num: int
    ) -> List[ProductData]:
        """
        Extract products from text content
        
        Args:
            text: Extracted text content
            page_num: Page number
            
        Returns:
            List of extracted products
        """
        products = []
        
        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Try different patterns
                product = self._extract_product_from_line(line, page_num)
                if product:
                    products.append(product)
            
            except Exception as e:
                self.logger.warning(f"Error extracting product from line: {e}")
                self.stats["warnings"] += 1
        
        return products
    
    def _create_product_from_row(
        self, 
        row: List[str], 
        column_map: Dict[str, int], 
        page_num: int
    ) -> Optional[ProductData]:
        """Create product from table row"""
        try:
            sku = str(row[column_map.get("sku", 0)]).strip() if column_map.get("sku") is not None else ""
            description = str(row[column_map.get("description", 1)]).strip() if column_map.get("description") is not None else ""
            size = str(row[column_map.get("size", 2)]).strip() if column_map.get("size") is not None else ""
            price_str = str(row[column_map.get("price", 3)]).strip() if column_map.get("price") is not None else ""
            
            # Validate SKU
            if not sku or not self.table_patterns["sku_pattern"].match(sku):
                return None
            
            # Parse price
            price = None
            if price_str:
                price_match = self.table_patterns["price_pattern"].search(price_str)
                if price_match:
                    price_str_clean = price_match.group().replace('$', '').replace(',', '')
                    try:
                        price = float(price_str_clean)
                    except ValueError:
                        pass
            
            # Determine unit
            unit = self.determine_unit(size, description)
            
            # Categorize product
            category = self.categorize_product(sku, description, None)
            
            # Assess construction relevance
            relevance = self.assess_construction_relevance(description, category)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(sku, description, size, price)
            
            return ProductData(
                sku=sku,
                product_name=description[:100],  # Truncate if too long
                description=description,
                size=size,
                unit=unit,
                price=price,
                category=category,
                page_number=page_num,
                confidence_score=confidence
            )
        
        except Exception as e:
            self.logger.warning(f"Error creating product from row: {e}")
            return None
    
    def _extract_product_from_line(
        self, 
        line: str, 
        page_num: int
    ) -> Optional[ProductData]:
        """Extract product from text line"""
        try:
            # Try product line pattern
            match = self.text_patterns["product_line"].search(line)
            if match:
                sku, description, price_str = match.groups()
                
                # Parse price
                price = None
                if price_str:
                    price_str_clean = price_str.replace('$', '').replace(',', '')
                    try:
                        price = float(price_str_clean)
                    except ValueError:
                        pass
                
                # Extract size from description
                size_match = self.text_patterns["size_extraction"].search(description)
                size = size_match.group(0) if size_match else ""
                
                # Determine unit
                unit = self.determine_unit(size, description)
                
                # Categorize product
                category = self.categorize_product(sku, description, None)
                
                # Assess construction relevance
                relevance = self.assess_construction_relevance(description, category)
                
                # Calculate confidence score
                confidence = self._calculate_confidence_score(sku, description, size, price)
                
                return ProductData(
                    sku=sku.strip(),
                    product_name=description[:100],
                    description=description.strip(),
                    size=size,
                    unit=unit,
                    price=price,
                    category=category,
                    page_number=page_num,
                    confidence_score=confidence
                )
            
            # Try SKU-description pattern
            match = self.text_patterns["sku_description"].search(line)
            if match:
                sku, description, price_str = match.groups()
                
                # Parse price if available
                price = None
                if price_str:
                    price_str_clean = price_str.replace('$', '').replace(',', '')
                    try:
                        price = float(price_str_clean)
                    except ValueError:
                        pass
                
                # Extract size from description
                size_match = self.text_patterns["size_extraction"].search(description)
                size = size_match.group(0) if size_match else ""
                
                # Determine unit
                unit = self.determine_unit(size, description)
                
                # Categorize product
                category = self.categorize_product(sku, description, None)
                
                # Assess construction relevance
                relevance = self.assess_construction_relevance(description, category)
                
                # Calculate confidence score
                confidence = self._calculate_confidence_score(sku, description, size, price)
                
                return ProductData(
                    sku=sku.strip(),
                    product_name=description[:100],
                    description=description.strip(),
                    size=size,
                    unit=unit,
                    price=price,
                    category=category,
                    page_number=page_num,
                    confidence_score=confidence
                )
        
        except Exception as e:
            self.logger.warning(f"Error extracting product from line: {e}")
            return None
        
        return None
    
    def categorize_product(
        self, 
        sku: str, 
        description: str, 
        current_category: Optional[str]
    ) -> ProductCategory:
        """
        Categorize product based on SKU and description
        
        Args:
            sku: Product SKU
            description: Product description
            current_category: Current category (if known)
            
        Returns:
            ProductCategory enum value
        """
        text_to_check = f"{sku} {description}".lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                return category
        
        return ProductCategory.UNKNOWN
    
    def determine_unit(self, size: str, description: str) -> str:
        """
        Determine the unit of measurement
        
        Args:
            size: Size string
            description: Product description
            
        Returns:
            Unit string (SQFT, LF, CY, EA, etc.)
        """
        text_to_check = f"{size} {description}".lower()
        
        # Check for area units
        if any(term in text_to_check for term in ["sq ft", "sqft", "square foot", "square feet"]):
            return "SQFT"
        elif any(term in text_to_check for term in ["sq yd", "sqyd", "square yard", "square yards"]):
            return "SQYD"
        
        # Check for linear units
        if any(term in text_to_check for term in ["linear foot", "linear feet", "lf", "foot", "feet"]):
            return "LF"
        elif any(term in text_to_check for term in ["linear yard", "linear yards", "ly", "yard", "yards"]):
            return "LY"
        
        # Check for volume units
        if any(term in text_to_check for term in ["cubic yard", "cubic yards", "cy", "yard³"]):
            return "CY"
        elif any(term in text_to_check for term in ["cubic foot", "cubic feet", "cf", "foot³"]):
            return "CF"
        
        # Check for weight units
        if any(term in text_to_check for term in ["pound", "pounds", "lb", "lbs"]):
            return "LB"
        elif any(term in text_to_check for term in ["ton", "tons"]):
            return "TON"
        
        # Check for count units
        if any(term in text_to_check for term in ["each", "piece", "pc", "pcs", "unit", "units"]):
            return "EA"
        
        # Default to EA if no clear unit
        return "EA"
    
    def assess_construction_relevance(
        self, 
        description: str, 
        category: ProductCategory
    ) -> str:
        """
        Assess construction relevance of product
        
        Args:
            description: Product description
            category: Product category
            
        Returns:
            Relevance level (high, medium, low)
        """
        # High relevance categories
        high_relevance = {
            ProductCategory.FORMWORK,
            ProductCategory.CONCRETE,
            ProductCategory.HARDWARE,
            ProductCategory.DRAINAGE
        }
        
        if category in high_relevance:
            return "high"
        
        # Medium relevance categories
        medium_relevance = {
            ProductCategory.LUMBER,
            ProductCategory.MASONRY,
            ProductCategory.DECORATIVE,
            ProductCategory.GEOSYNTHETICS
        }
        
        if category in medium_relevance:
            return "medium"
        
        # Check description keywords
        construction_keywords = {
            "construction", "building", "contractor", "jobsite", "project",
            "form", "concrete", "steel", "rebar", "anchor", "fastener"
        }
        
        description_lower = description.lower()
        if any(keyword in description_lower for keyword in construction_keywords):
            return "medium"
        
        return "low"
    
    def _calculate_confidence_score(
        self, 
        sku: str, 
        description: str, 
        size: str, 
        price: Optional[float]
    ) -> float:
        """Calculate confidence score for extracted product"""
        score = 0.0
        
        # SKU validation
        if sku and self.table_patterns["sku_pattern"].match(sku):
            score += 0.3
        
        # Description quality
        if description and len(description.strip()) > 10:
            score += 0.2
        
        # Size information
        if size and len(size.strip()) > 0:
            score += 0.2
        
        # Price information
        if price is not None and price > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the extracted DataFrame
        
        Args:
            df: Raw extracted DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['sku'], keep='first')
        
        # Clean SKU column
        df['sku'] = df['sku'].astype(str).str.strip().str.upper()
        
        # Clean description column
        df['description'] = df['description'].astype(str).str.strip()
        df['description'] = df['description'].replace('nan', '')
        
        # Clean size column
        df['size'] = df['size'].astype(str).str.strip()
        df['size'] = df['size'].replace('nan', '')
        
        # Standardize unit column
        df['unit'] = df['unit'].astype(str).str.upper()
        
        # Clean price column
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Convert category to string
        df['category'] = df['category'].astype(str)
        
        # Add extraction metadata
        df['extracted_at'] = datetime.now()
        df['source'] = 'whitecap_catalog'
        
        # Filter by confidence score
        if 'confidence_score' in df.columns:
            df = df[df['confidence_score'] >= self.config.min_confidence_score]
        
        # Sort by category priority and confidence
        category_priority = {
            ProductCategory.FORMWORK.value: 1,
            ProductCategory.CONCRETE.value: 2,
            ProductCategory.HARDWARE.value: 3,
            ProductCategory.DRAINAGE.value: 4,
            ProductCategory.LUMBER.value: 5,
            ProductCategory.MASONRY.value: 6,
            ProductCategory.DECORATIVE.value: 7,
            ProductCategory.GEOSYNTHETICS.value: 8,
            ProductCategory.TOOLS.value: 9,
            ProductCategory.SAFETY.value: 10,
            ProductCategory.UNKNOWN.value: 11
        }
        
        df['category_priority'] = df['category'].map(category_priority).fillna(11)
        df = df.sort_values(['category_priority', 'confidence_score'], ascending=[True, False])
        df = df.drop('category_priority', axis=1)
        
        return df
    
    def export_to_csv(self, df: pd.DataFrame, output_path: Union[str, Path]) -> None:
        """
        Export DataFrame to CSV file
        
        Args:
            df: DataFrame to export
            output_path: Output file path
        """
        output_path = Path(output_path)
        
        try:
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export to CSV
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Data exported to {output_path}: {len(df)} products")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            **self.stats,
            "progress": self.progress_tracker.get_progress() if self.progress_tracker else None
        }


# Convenience functions
def extract_whitecap_catalog(pdf_path: Union[str, Path]) -> pd.DataFrame:
    """Convenience function for catalog extraction"""
    extractor = WhitecapCatalogExtractor()
    return extractor.extract_catalog_data(pdf_path)


def extract_whitecap_sections(
    pdf_path: Union[str, Path], 
    sections: List[str]
) -> pd.DataFrame:
    """Convenience function for section-based extraction"""
    extractor = WhitecapCatalogExtractor()
    
    # Build sections config
    sections_config = {}
    for section in sections:
        sections_config[section] = {"enabled": True}
    
    return extractor.extract_by_sections(pdf_path, sections_config)


if __name__ == "__main__":
    # Example usage
    extractor = WhitecapCatalogExtractor()
    
    # Extract critical sections
    critical_sections = ["concrete_forming", "fastening_systems", "decorative_concrete"]
    
    try:
        # Extract from specific sections
        df = extractor.extract_by_sections("whitecap_catalog.pdf", {
            section: {"enabled": True} for section in critical_sections
        })
        
        # Export results
        extractor.export_to_csv(df, "output/catalogs/whitecap_critical_products.csv")
        
        # Print statistics
        stats = extractor.get_extraction_stats()
        print(f"Extraction completed: {stats}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        traceback.print_exc() 