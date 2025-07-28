"""
Whitecap Online Catalog Extractor for PACE - Project Analysis & Construction Estimating

This module provides functionality to extract product information from Whitecap's
online catalog at whitecap.com for use in the PACE construction bidding automation platform.

The extractor supports:
- Web scraping of product categories and subcategories
- Product information extraction from listing pages
- Pricing and availability data collection
- Multi-format export capabilities
- Rate limiting and respectful scraping

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
import time
import random

# Third-party imports
try:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse, parse_qs
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from fake_useragent import UserAgent
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    print("Warning: Web scraping dependencies not installed. Install with: pip install requests beautifulsoup4 selenium lxml webdriver-manager fake-useragent")

# Local imports
try:
    from src.utils.data_validator import DataValidator, ValidationResult, ProgressTracker
except ImportError:
    # Fallback if data_validator is not available
    class DataValidator:
        def __init__(self, logger=None):
            self.logger = logger or logging.getLogger(__name__)
    
    class ValidationResult:
        def __init__(self, is_valid=True, level="info", message="", details=None):
            self.is_valid = is_valid
            self.level = level
            self.message = message
            self.details = details or {}
    
    class ProgressTracker:
        def __init__(self, total_items=0):
            self.total_items = total_items
            self.current_item = 0
        
        def update(self, item_id: str, success: bool = True, message: str = "") -> None:
            """Update progress for an item"""
            self.current_item += 1
        
        def get_progress(self):
            return {"current_item": self.current_item, "total_items": self.total_items}

try:
    from config.settings import get_setting
except ImportError:
    def get_setting(key, default=None):
        return default


class ProductCategory(Enum):
    """Product categories for Whitecap online catalog"""
    ADHESIVES = "adhesives"
    CAULK_SEALANTS = "caulk_sealants"
    ANCHORING_FASTENERS = "anchoring_fasteners"
    BRICK_STONE = "brick_stone"
    BUILDING_MATERIALS = "building_materials"
    CLEANING_TOOLS = "cleaning_tools"
    CONCRETE_CHEMICALS = "concrete_chemicals"
    CONCRETE_FORMING = "concrete_forming"
    ELECTRICAL_LIGHTING = "electrical_lighting"
    EROSION_CONTROL = "erosion_control"
    HAND_TOOLS = "hand_tools"
    JOBSITE_SUPPLIES = "jobsite_supplies"
    LADDERS_SCAFFOLDING = "ladders_scaffolding"
    MASONRY_BLOCK = "masonry_block"
    MATERIAL_HANDLING = "material_handling"
    MEASURING_MARKING = "measuring_marking"
    POWER_TOOLS = "power_tools"
    SAFETY = "safety"
    WATERPROOFING = "waterproofing"
    SPECIALS_DEALS = "specials_deals"
    UNKNOWN = "unknown"


class ExtractionPriority(Enum):
    """Extraction priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class OnlineProductData:
    """Standardized online product data structure"""
    sku: str
    product_name: str
    description: str
    size: str
    unit: str
    price: Optional[float] = None
    category: ProductCategory = ProductCategory.UNKNOWN
    subcategory: Optional[str] = None
    priority: ExtractionPriority = ExtractionPriority.LOW
    url: Optional[str] = None
    availability: str = "unknown"
    branch_location: Optional[str] = None
    mfg_number: Optional[str] = None
    construction_relevance: str = "low"
    extracted_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0


@dataclass
class OnlineExtractionConfig:
    """Configuration for online catalog extraction"""
    base_url: str = "https://www.whitecap.com"
    categories_to_extract: List[str] = field(default_factory=lambda: [])  # Empty means all categories
    max_products_per_category: int = 1000  # Increased for full catalog
    min_confidence_score: float = 0.5  # Lowered for broader extraction
    enable_progress_tracking: bool = True
    enable_validation: bool = True
    export_format: str = "csv"
    rate_limit_delay: float = 3.0  # Increased to 3 seconds between requests
    use_selenium: bool = True  # Enable Selenium for better human-like behavior
    headless_browser: bool = False  # Show browser for more human-like appearance
    timeout_seconds: int = 30
    max_retries: int = 3
    save_progress: bool = True
    progress_file: str = "extraction_progress.json"
    # Human-like behavior settings
    human_like_delays: bool = True
    min_page_load_delay: float = 2.0  # Minimum time to wait after page load
    max_page_load_delay: float = 5.0  # Maximum time to wait after page load
    min_scroll_delay: float = 0.5  # Minimum time between scrolls
    max_scroll_delay: float = 2.0  # Maximum time between scrolls
    min_click_delay: float = 1.0  # Minimum time before clicking
    max_click_delay: float = 3.0  # Maximum time before clicking


class WhitecapOnlineExtractor:
    """
    Extractor for Whitecap's online catalog
    
    Handles web scraping of product categories, subcategories, and individual products
    from the Whitecap website.
    """
    
    def __init__(self, config: Optional[OnlineExtractionConfig] = None):
        """
        Initialize the online extractor
        
        Args:
            config: Configuration for extraction
        """
        self.config = config or OnlineExtractionConfig()
        self.logger = self._setup_logger()
        self.session = None
        self.driver = None
        self.stats = {
            "total_products": 0,
            "categories_processed": 0,
            "products_extracted": 0,
            "errors": 0,
            "start_time": datetime.now(),
            "end_time": None
        }
        
        self.progress_tracker = ProgressTracker(0) if self.config.enable_progress_tracking else None
        self.validator = DataValidator() if self.config.enable_validation else None
        
        # Category mapping based on the screenshots
        self.category_mapping = {
            "Adhesives, Caulk and Sealants": ProductCategory.ADHESIVES,
            "Anchoring and Fasteners": ProductCategory.ANCHORING_FASTENERS,
            "Brick and Stone": ProductCategory.BRICK_STONE,
            "Building Materials": ProductCategory.BUILDING_MATERIALS,
            "Cleaning Tools and Supplies": ProductCategory.CLEANING_TOOLS,
            "Concrete and Chemicals": ProductCategory.CONCRETE_CHEMICALS,
            "Concrete Forming and Accessories": ProductCategory.CONCRETE_FORMING,
            "Electrical and Lighting": ProductCategory.ELECTRICAL_LIGHTING,
            "Erosion Control and Geosynthetics": ProductCategory.EROSION_CONTROL,
            "Hand Tools": ProductCategory.HAND_TOOLS,
            "Jobsite Supplies and Security": ProductCategory.JOBSITE_SUPPLIES,
            "Ladders and Scaffolding": ProductCategory.LADDERS_SCAFFOLDING,
            "Masonry Block, Pavers, Mortars and Accessories": ProductCategory.MASONRY_BLOCK,
            "Material Handling and Storage": ProductCategory.MATERIAL_HANDLING,
            "Measuring, Marking and Surveying": ProductCategory.MEASURING_MARKING,
            "Power Tool and Equipment Accessories": ProductCategory.POWER_TOOLS,
            "Power Tools and Equipment": ProductCategory.POWER_TOOLS,
            "Safety": ProductCategory.SAFETY,
            "Waterproofing": ProductCategory.WATERPROOFING,
            "Specials and Deals": ProductCategory.SPECIALS_DEALS
        }
        
        # Load progress if available
        self.extracted_products = set()
        self.processed_categories = set()
        if self.config.save_progress:
            self._load_progress()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _human_like_delay(self, min_delay: float = None, max_delay: float = None):
        """Add a human-like random delay"""
        if not self.config.human_like_delays:
            return
        
        if min_delay is None:
            min_delay = self.config.min_page_load_delay
        if max_delay is None:
            max_delay = self.config.max_page_load_delay
        
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"Human-like delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    def _human_like_scroll(self, driver):
        """Perform human-like scrolling on the page"""
        if not self.config.human_like_delays or not driver:
            return
        
        try:
            # Get page height
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # Scroll down gradually like a human would
            current_position = 0
            while current_position < page_height:
                # Random scroll amount (like human scrolling)
                scroll_amount = random.randint(300, 800)
                current_position += scroll_amount
                
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                
                # Random delay between scrolls
                scroll_delay = random.uniform(
                    self.config.min_scroll_delay, 
                    self.config.max_scroll_delay
                )
                time.sleep(scroll_delay)
                
                # Sometimes pause longer (like reading content)
                if random.random() < 0.3:  # 30% chance
                    pause_delay = random.uniform(1.0, 3.0)
                    time.sleep(pause_delay)
            
            # Scroll back to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            self.logger.debug(f"Error during human-like scrolling: {e}")
    
    def _human_like_click(self, element, driver):
        """Perform human-like clicking on an element"""
        if not self.config.human_like_delays or not driver:
            return element
        
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            
            # Random delay before clicking
            click_delay = random.uniform(
                self.config.min_click_delay, 
                self.config.max_click_delay
            )
            time.sleep(click_delay)
            
            # Click the element
            element.click()
            
        except Exception as e:
            self.logger.debug(f"Error during human-like clicking: {e}")
        
        return element
    
    def _setup_session(self):
        """Setup requests session with proper headers"""
        if not WEB_SCRAPING_AVAILABLE:
            return None
            
        self.session = requests.Session()
        
        # Use fake user agent
        try:
            ua = UserAgent()
            user_agent = ua.random
        except:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _setup_selenium_driver(self) -> Optional[webdriver.Chrome]:
        """Setup Selenium WebDriver for dynamic content"""
        if not WEB_SCRAPING_AVAILABLE:
            return None
            
        try:
            chrome_options = Options()
            
            if self.config.headless_browser:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to handle driver installation
            driver_path = ChromeDriverManager().install()
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.set_page_load_timeout(self.config.timeout_seconds)
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {e}")
            return None
    
    def _load_progress(self):
        """Load extraction progress from file"""
        progress_file = Path(self.config.progress_file)
        if progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                    self.extracted_products = set(progress_data.get('extracted_products', []))
                    self.processed_categories = set(progress_data.get('processed_categories', []))
                    self.logger.info(f"Loaded progress: {len(self.extracted_products)} products, {len(self.processed_categories)} categories")
            except Exception as e:
                self.logger.warning(f"Could not load progress file: {e}")
    
    def _save_progress(self):
        """Save extraction progress to file"""
        if not self.config.save_progress:
            return
            
        try:
            progress_data = {
                'extracted_products': list(self.extracted_products),
                'processed_categories': list(self.processed_categories),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.config.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not save progress: {e}")
    
    def extract_catalog_data(self) -> pd.DataFrame:
        """
        Extract product data from Whitecap's online catalog
        
        Returns:
            DataFrame containing extracted product information
        """
        self.logger.info("Starting online catalog extraction from Whitecap")
        
        if not WEB_SCRAPING_AVAILABLE:
            self.logger.warning("Web scraping not available. Using sample data.")
            return self._create_sample_data()
        
        try:
            # Setup web scraping tools
            self._setup_session()
            if self.config.use_selenium:
                self.driver = self._setup_selenium_driver()
            
            all_products = []
            
            # Get main categories
            categories = self._get_main_categories()
            self.logger.info(f"Found {len(categories)} main categories")
            
            if self.progress_tracker:
                self.progress_tracker.total_items = len(categories)
            
            for category_name, category_url in categories.items():
                if category_name in self.processed_categories:
                    self.logger.info(f"Skipping already processed category: {category_name}")
                    continue
                
                if self.progress_tracker:
                    self.progress_tracker.update(
                        category_name, 
                        success=True, 
                        message=f"Processing category: {category_name}"
                    )
                
                try:
                    category_products = self._extract_category_products(category_name, category_url)
                    all_products.extend(category_products)
                    
                    # Only mark as processed if we actually got products
                    if category_products:
                        self.stats["categories_processed"] += 1
                        self.processed_categories.add(category_name)
                        self.logger.info(f"✅ Extracted {len(category_products)} products from {category_name}")
                    else:
                        self.logger.warning(f"⚠️  No products found in category: {category_name}")
                    
                    # Save progress periodically
                    if self.config.save_progress and self.stats["categories_processed"] % 5 == 0:
                        self._save_progress()
                    
                    # Human-like delay between categories
                    self.logger.info(f"Completed category: {category_name}. Taking a break...")
                    self._human_like_delay(5.0, 10.0)  # Longer delay between categories
                    
                except Exception as e:
                    self.logger.error(f"Error processing category {category_name}: {e}")
                    self.stats["errors"] += 1
                    continue
            
            # Convert to DataFrame
            df = pd.DataFrame([vars(product) for product in all_products])
            
            if len(df) > 0:
                df = self.clean_dataframe(df)
            
            self.stats["total_products"] = len(df)
            self.stats["end_time"] = datetime.now()
            
            self.logger.info(f"Extraction completed: {len(df)} products extracted")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
            if self.config.save_progress:
                self._save_progress()
    
    def _get_main_categories(self) -> Dict[str, str]:
        """
        Extract main category names and URLs from the catalog
        
        Returns:
            Dictionary mapping category names to URLs
        """
        categories = {}
        
        try:
            if self.config.use_selenium and self.driver:
                self.logger.info("Navigating to Whitecap homepage...")
                self.driver.get(self.config.base_url)
                
                # Human-like delay after page load
                self._human_like_delay()
                
                # Perform human-like scrolling to load all content
                self._human_like_scroll(self.driver)
                
                # Additional delay after scrolling
                self._human_like_delay(1.0, 2.0)
                
                # Look for category navigation elements
                category_selectors = [
                    "nav a[href*='category']",
                    ".category-nav a", 
                    ".main-nav a",
                    ".navigation a",
                    "a[href*='/category/']",
                    "a[href*='/products/']"
                ]
                
                for selector in category_selectors:
                    try:
                        category_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in category_elements:
                            category_name = element.text.strip()
                            category_url = element.get_attribute('href')
                            
                            if category_name and category_url and len(category_name) > 2:
                                categories[category_name] = category_url
                    except Exception as e:
                        self.logger.debug(f"Selector {selector} failed: {e}")
                        continue
                        
            else:
                # Fallback to requests
                response = self.session.get(self.config.base_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for category links with the specific Whitecap URL pattern
                category_links = soup.find_all('a', href=re.compile(r'/catalog/.*-en'))
                
                # Also look for navigation menu items that might contain categories
                nav_links = soup.find_all('a', href=True)
                
                # Define known product categories based on the screenshot
                known_categories = [
                    'adhesives', 'caulk', 'sealants', 'anchoring', 'fasteners', 'brick', 'stone',
                    'building materials', 'cleaning', 'tools', 'supplies', 'concrete', 'chemicals',
                    'forming', 'electrical', 'lighting', 'erosion', 'control', 'hand tools',
                    'jobsite', 'security', 'ladders', 'scaffolding', 'masonry', 'block', 'pavers',
                    'mortars', 'material handling', 'storage', 'measuring', 'marking', 'surveying',
                    'power tools', 'equipment', 'safety', 'waterproofing', 'specials', 'deals'
                ]
                
                # Process catalog links first (these are the main product categories)
                for link in category_links:
                    category_name = link.text.strip()
                    category_url = urljoin(self.config.base_url, link.get('href'))
                    
                    if category_name and category_url and len(category_name) > 2:
                        categories[category_name] = category_url
                
                # If we didn't find enough categories, try navigation links
                if len(categories) < 5:
                    for link in nav_links:
                        category_name = link.text.strip()
                        category_url = urljoin(self.config.base_url, link.get('href'))
                        
                        # Filter for actual product categories
                        if (category_name and category_url and len(category_name) > 2 and
                            any(keyword in category_name.lower() for keyword in known_categories) and
                            'catalog' in category_url.lower()):
                            categories[category_name] = category_url
            
            # Filter to only include categories we want to extract
            if self.config.categories_to_extract:
                filtered_categories = {}
                for name, url in categories.items():
                    for target_category in self.config.categories_to_extract:
                        if target_category.lower() in name.lower():
                            filtered_categories[name] = url
                            break
                categories = filtered_categories
            
            # If we still don't have enough categories, add some known ones as fallback
            if len(categories) < 10:
                known_category_urls = {
                    "Adhesives, Caulk and Sealants": "https://www.whitecap.com/catalog/Adhesives-Caulk-and-Sealants-en",
                    "Anchoring and Fasteners": "https://www.whitecap.com/catalog/Anchoring-and-Fasteners-en",
                    "Brick and Stone": "https://www.whitecap.com/catalog/Brick-and-Stone-en",
                    "Building Materials": "https://www.whitecap.com/catalog/Building-Materials-en",
                    "Cleaning Tools and Supplies": "https://www.whitecap.com/catalog/Cleaning-Tools-and-Supplies-en",
                    "Concrete and Chemicals": "https://www.whitecap.com/catalog/Concrete-and-Chemicals-en",
                    "Concrete Forming and Accessories": "https://www.whitecap.com/catalog/Concrete-Forming-and-Accessories-en",
                    "Electrical and Lighting": "https://www.whitecap.com/catalog/Electrical-and-Lighting-en",
                    "Erosion Control and Geosynthetics": "https://www.whitecap.com/catalog/Erosion-Control-and-Geosynthetics-en",
                    "Hand Tools": "https://www.whitecap.com/catalog/Hand-Tools-en",
                    "Jobsite Supplies and Security": "https://www.whitecap.com/catalog/Jobsite-Supplies-and-Security-en",
                    "Ladders and Scaffolding": "https://www.whitecap.com/catalog/Ladders-and-Scaffolding-en",
                    "Masonry Block, Pavers, Mortars and Accessories": "https://www.whitecap.com/catalog/Masonry-Block-Pavers-Mortars-and-Accessories-en",
                    "Material Handling and Storage": "https://www.whitecap.com/catalog/Material-Handling-and-Storage-en",
                    "Measuring, Marking and Surveying": "https://www.whitecap.com/catalog/Measuring-Marking-and-Surveying-en",
                    "Power Tool and Equipment Accessories": "https://www.whitecap.com/catalog/Power-Tool-and-Equipment-Accessories-en",
                    "Power Tools and Equipment": "https://www.whitecap.com/catalog/Power-Tools-and-Equipment-en",
                    "Safety": "https://www.whitecap.com/catalog/Safety-en",
                    "Waterproofing": "https://www.whitecap.com/catalog/Waterproofing-en"
                }
                
                for name, url in known_category_urls.items():
                    if name not in categories:
                        categories[name] = url
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting main categories: {e}")
            return {}
    
    def _extract_category_products(self, category_name: str, category_url: str) -> List[OnlineProductData]:
        """
        Extract products from a specific category
        
        Args:
            category_name: Name of the category
            category_url: URL of the category page
            
        Returns:
            List of product data objects
        """
        products = []
        
        try:
            # First, get subcategories from the main category page
            subcategories = self._get_subcategories(category_name, category_url)
            self.logger.info(f"Found {len(subcategories)} subcategories in {category_name}")
            
            if not subcategories:
                self.logger.warning(f"No subcategories found in {category_name}, trying direct product extraction")
                # Try direct product extraction as fallback
                return self._extract_products_direct(category_name, category_url)
            
            # Extract products from each subcategory
            for subcategory_name, subcategory_url in subcategories.items():
                try:
                    self.logger.info(f"Extracting products from subcategory: {subcategory_name}")
                    
                    # Get sub-subcategories from the subcategory page
                    sub_subcategories = self._get_subcategories(subcategory_name, subcategory_url)
                    self.logger.info(f"Found {len(sub_subcategories)} sub-subcategories in {subcategory_name}")
                    
                    if sub_subcategories:
                        # Extract products from each sub-subcategory
                        for sub_subcategory_name, sub_subcategory_url in sub_subcategories.items():
                            try:
                                self.logger.info(f"Extracting products from sub-subcategory: {sub_subcategory_name}")
                                sub_subcategory_products = self._extract_products_direct(sub_subcategory_name, sub_subcategory_url)
                                products.extend(sub_subcategory_products)
                                
                                if sub_subcategory_products:
                                    self.logger.info(f"✅ Extracted {len(sub_subcategory_products)} products from {sub_subcategory_name}")
                                else:
                                    self.logger.warning(f"⚠️  No products found in sub-subcategory: {sub_subcategory_name}")
                                
                                # Human-like delay between sub-subcategories
                                self._human_like_delay(2.0, 4.0)
                                
                            except Exception as e:
                                self.logger.error(f"Error extracting from sub-subcategory {sub_subcategory_name}: {e}")
                                continue
                    else:
                        # Try direct extraction from subcategory if no sub-subcategories found
                        subcategory_products = self._extract_products_direct(subcategory_name, subcategory_url)
                        products.extend(subcategory_products)
                        
                        if subcategory_products:
                            self.logger.info(f"✅ Extracted {len(subcategory_products)} products from {subcategory_name}")
                        else:
                            self.logger.warning(f"⚠️  No products found in subcategory: {subcategory_name}")
                    
                    # Human-like delay between subcategories
                    self._human_like_delay(3.0, 6.0)
                    
                except Exception as e:
                    self.logger.error(f"Error extracting from subcategory {subcategory_name}: {e}")
                    continue
            
            return products[:self.config.max_products_per_category]
            
        except Exception as e:
            self.logger.error(f"Error extracting products from category {category_name}: {e}")
            return []
    
    def _get_subcategories(self, category_name: str, category_url: str) -> Dict[str, str]:
        """
        Extract subcategory names and URLs from a category page
        
        Args:
            category_name: Name of the category
            category_url: URL of the category page
            
        Returns:
            Dictionary mapping subcategory names to URLs
        """
        subcategories = {}
        
        try:
            if self.config.use_selenium and self.driver:
                self.logger.info(f"Navigating to category page: {category_name}")
                self.driver.get(category_url)
                
                # Human-like delay after page load
                self._human_like_delay()
                
                # Perform human-like scrolling to load all content
                self._human_like_scroll(self.driver)
                
                # Additional delay after scrolling
                self._human_like_delay(1.0, 2.0)
                
                # Look for subcategory links
                subcategory_selectors = [
                    "a[href*='/catalog/']",
                    ".StyledButton[href*='/catalog/']",
                    "a[data-test-selector*='categoryDetailsSubCategoriesLink']"
                ]
                
                for selector in subcategory_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            subcategory_name = element.text.strip()
                            subcategory_url = element.get_attribute('href')
                            
                            if (subcategory_name and subcategory_url and 
                                len(subcategory_name) > 2 and 
                                subcategory_url != category_url and
                                '/catalog/' in subcategory_url):
                                subcategories[subcategory_name] = subcategory_url
                    except Exception as e:
                        self.logger.debug(f"Selector {selector} failed: {e}")
                        continue
                        
            else:
                # Fallback to requests
                response = self.session.get(category_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for subcategory links
                subcategory_links = soup.find_all('a', href=re.compile(r'/catalog/.*-en'))
                
                for link in subcategory_links:
                    subcategory_name = link.text.strip()
                    subcategory_url = urljoin(self.config.base_url, link.get('href'))
                    
                    if (subcategory_name and subcategory_url and 
                        len(subcategory_name) > 2 and 
                        subcategory_url != category_url):
                        subcategories[subcategory_name] = subcategory_url
            
            return subcategories
            
        except Exception as e:
            self.logger.error(f"Error getting subcategories for {category_name}: {e}")
            return {}
    
    def _extract_products_direct(self, category_name: str, category_url: str) -> List[OnlineProductData]:
        """
        Extract products directly from a category/subcategory page
        
        Args:
            category_name: Name of the category/subcategory
            category_url: URL of the category/subcategory page
            
        Returns:
            List of product data objects
        """
        products = []
        page_num = 1
        
        try:
            while len(products) < self.config.max_products_per_category:
                page_url = f"{category_url}?page={page_num}" if page_num > 1 else category_url
                
                if self.config.use_selenium and self.driver:
                    self.logger.info(f"Loading page {page_num} for {category_name}")
                    self.driver.get(page_url)
                    
                    # Human-like delay after page load
                    self._human_like_delay()
                    
                    # Perform human-like scrolling to load all content
                    self._human_like_scroll(self.driver)
                    
                    # Additional delay after scrolling
                    self._human_like_delay(1.0, 2.0)
                    
                    # Wait for product listings to load - updated selectors for Whitecap
                    try:
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 
                                ".product-item, .product-listing, .item, .product-card, [data-test-selector*='product'], div[class*='GridItemStyle']"))
                        )
                    except TimeoutException:
                        self.logger.warning(f"No products found on page {page_num} for {category_name}")
                        break
                    
                    # Extract products from current page
                    page_products = self._extract_products_from_page(category_name)
                    
                    if not page_products:
                        # Try to check if this is actually a product listing page or just another category page
                        page_source = self.driver.page_source
                        if 'product' in page_source.lower() or '$' in page_source:
                            self.logger.info(f"Page contains product indicators but no products extracted - may need different selectors")
                        break
                    
                    products.extend(page_products)
                    
                else:
                    # Fallback to requests
                    response = self.session.get(page_url)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_products = self._extract_products_from_soup(soup, category_name)
                    
                    if not page_products:
                        # Check if page contains product indicators
                        page_text = soup.get_text().lower()
                        if 'product' in page_text or '$' in page_text:
                            self.logger.info(f"Page contains product indicators but no products extracted - may need different selectors")
                        break
                    
                    products.extend(page_products)
                
                page_num += 1
                time.sleep(self.config.rate_limit_delay)
            
            return products[:self.config.max_products_per_category]
            
        except Exception as e:
            self.logger.error(f"Error extracting products directly from {category_name}: {e}")
            return []
    
    def _extract_products_from_page(self, category_name: str) -> List[OnlineProductData]:
        """
        Extract products from the current page using Selenium
        
        Args:
            category_name: Name of the category
            
        Returns:
            List of product data objects
        """
        products = []
        
        try:
            # Find product containers - updated for Whitecap's React structure
            product_selectors = [
                ".product-item",
                ".product-listing", 
                ".item",
                ".product-card",
                ".product",
                "[data-product-id]",
                "[data-test-selector*='product']",
                ".GridItemStyle-sc-1uambol",  # From the HTML we saw
                "div[class*='product']",
                "div[class*='item']",
                "div[class*='card']",
                "article",
                "section"
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        product_elements = elements
                        break
                except Exception:
                    continue
            
            for element in product_elements:
                try:
                    product_data = self._extract_single_product(element, category_name)
                    if product_data and product_data.sku not in self.extracted_products:
                        products.append(product_data)
                        self.extracted_products.add(product_data.sku)
                except Exception as e:
                    self.logger.warning(f"Error extracting individual product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting products from page: {e}")
            return []
    
    def _extract_products_from_soup(self, soup: BeautifulSoup, category_name: str) -> List[OnlineProductData]:
        """
        Extract products from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object of the page
            category_name: Name of the category
            
        Returns:
            List of product data objects
        """
        products = []
        
        try:
            # First, try to extract from JavaScript data (this is more reliable for Whitecap)
            self.logger.info("Attempting to extract products from JavaScript data")
            products = self._extract_products_from_javascript_data(soup, category_name)
            
            # If no products found in JavaScript data, try traditional HTML selectors
            if not products:
                self.logger.info("No products found in JavaScript data, trying traditional HTML selectors")
                
                # Updated selectors for Whitecap's React structure
                product_selectors = [
                    # Look for GridItemStyle elements that might contain products
                    'div[class*="GridItemStyle"]',
                    # Look for elements with product-related data attributes
                    '[data-test-selector*="product"]',
                    '[data-testid*="product"]',
                    # Look for elements with product-related classes
                    '.product-item', '.product-listing', '.item', '.product-card',
                    '.catalog-item', '.catalog-product', '.search-result',
                    # Look for any div with product-related text
                    'div:contains("SKU")', 'div:contains("Price")', 'div:contains("$")'
                ]
            
            product_elements = []
            
            for selector in product_selectors:
                try:
                    if ':contains(' in selector:
                        # Handle :contains pseudo-selector manually
                        if 'SKU' in selector:
                            elements = soup.find_all('div', text=re.compile(r'SKU|sku', re.I))
                        elif 'Price' in selector:
                            elements = soup.find_all('div', text=re.compile(r'Price|price', re.I))
                        elif '$' in selector:
                            elements = soup.find_all('div', text=re.compile(r'\$[\d,]+\.?\d*'))
                        else:
                            continue
                    else:
                        elements = soup.select(selector)
                    
                    product_elements.extend(elements)
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_elements = []
            for element in product_elements:
                if element not in seen:
                    seen.add(element)
                    unique_elements.append(element)
            
            self.logger.info(f"Found {len(unique_elements)} potential product elements in {category_name}")
            
            # If still no products found, try to find any elements with prices
            if not unique_elements:
                self.logger.warning(f"No products found with standard selectors in {category_name}, searching for price elements")
                price_elements = soup.find_all(text=re.compile(r'\$[\d,]+\.?\d*'))
                if price_elements:
                    self.logger.info(f"Found {len(price_elements)} elements with prices in {category_name}")
                    # Get parent elements of price text
                    for price_text in price_elements[:10]:  # Limit to first 10
                        parent = price_text.parent
                        if parent and parent not in unique_elements:
                            unique_elements.append(parent)
            
            for element in unique_elements:
                try:
                    product_data = self._extract_single_product_from_soup(element, category_name)
                    if product_data and product_data.sku not in self.extracted_products:
                        products.append(product_data)
                        self.extracted_products.add(product_data.sku)
                except Exception as e:
                    self.logger.warning(f"Error extracting individual product: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(products)} products from {category_name}")
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting products from soup: {e}")
            return []
    
    def _extract_products_from_javascript_data(self, soup: BeautifulSoup, category_name: str) -> List[OnlineProductData]:
        """
        Extract products from JavaScript data embedded in the HTML
        
        Args:
            soup: BeautifulSoup object of the page
            category_name: Name of the category
            
        Returns:
            List of product data objects
        """
        products = []
        
        try:
            # Look for script tags that might contain product data
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                script_content = script.string
                if not script_content:
                    continue
                
                # Look for product data patterns in JavaScript
                # Pattern 1: productInfosById object
                product_info_pattern = r'"productInfosById":\s*\{([^}]+)\}'
                product_info_matches = re.findall(product_info_pattern, script_content, re.DOTALL)
                
                for match in product_info_matches:
                    # Extract individual product data
                    product_pattern = r'"([a-f0-9\-]+)":\s*\{([^}]+)\}'
                    product_matches = re.findall(product_pattern, match, re.DOTALL)
                    
                    for product_id, product_data in product_matches:
                        try:
                            # Extract product information
                            product_name_match = re.search(r'"productName":\s*"([^"]+)"', product_data)
                            title_match = re.search(r'"title":\s*"([^"]+)"', product_data)
                            sku_match = re.search(r'"sku":\s*"([^"]+)"', product_data)
                            
                            # Extract pricing information
                            pricing_pattern = r'"pricing":\s*\{([^}]+)\}'
                            pricing_match = re.search(pricing_pattern, product_data, re.DOTALL)
                            
                            price = None
                            if pricing_match:
                                price_match = re.search(r'"unitListPrice":\s*([\d\.]+)', pricing_match.group(1))
                                if price_match:
                                    price = float(price_match.group(1))
                            
                            # Create product data object
                            if product_name_match or title_match:
                                product_name = product_name_match.group(1) if product_name_match else title_match.group(1)
                                sku = sku_match.group(1) if sku_match else product_name
                                
                                # Extract size and unit from product name
                                size = self._extract_size(product_name)
                                unit = self._determine_unit(product_name)
                                
                                # Create product data
                                product_data_obj = OnlineProductData(
                                    sku=sku,
                                    product_name=product_name,
                                    description=title_match.group(1) if title_match else product_name,
                                    size=size,
                                    unit=unit,
                                    price=price,
                                    category=self._map_category(category_name),
                                    subcategory=category_name,
                                    url=f"{self.config.base_url}/product/{sku.lower()}",
                                    confidence_score=0.8 if price else 0.6
                                )
                                
                                if product_data_obj.sku not in self.extracted_products:
                                    products.append(product_data_obj)
                                    self.extracted_products.add(product_data_obj.sku)
                                    self.logger.debug(f"Extracted product from JavaScript: {product_name} (SKU: {sku})")
                        
                        except Exception as e:
                            self.logger.debug(f"Error parsing individual product data: {e}")
                            continue
                
                # Pattern 2: Look for product data in other JavaScript objects
                # This is a more general pattern for finding product information
                general_product_pattern = r'"productId":\s*"([^"]+)".*?"productName":\s*"([^"]+)".*?"title":\s*"([^"]+)".*?"sku":\s*"([^"]+)"'
                general_matches = re.findall(general_product_pattern, script_content, re.DOTALL)
                
                for product_id, product_name, title, sku in general_matches:
                    try:
                        # Extract price if available
                        price_pattern = rf'"productId":\s*"{re.escape(product_id)}".*?"unitListPrice":\s*([\d\.]+)'
                        price_match = re.search(price_pattern, script_content, re.DOTALL)
                        price = float(price_match.group(1)) if price_match else None
                        
                        # Extract size and unit from the full title
                        size = self._extract_size(title)
                        unit = self._determine_unit(title)
                        
                        # Create product data
                        product_data_obj = OnlineProductData(
                            sku=sku,
                            product_name=title,  # Use the full title instead of just productName
                            description=title,
                            size=size,
                            unit=unit,
                            price=price,
                            category=self._map_category(category_name),
                            subcategory=category_name,
                            url=f"{self.config.base_url}/product/{sku.lower()}",
                            confidence_score=0.8 if price else 0.6
                        )
                        
                        if product_data_obj.sku not in self.extracted_products:
                            products.append(product_data_obj)
                            self.extracted_products.add(product_data_obj.sku)
                            self.logger.debug(f"Extracted product from general pattern: {title} (SKU: {sku})")
                    
                    except Exception as e:
                        self.logger.debug(f"Error parsing general product pattern: {e}")
                        continue
            
            self.logger.info(f"Extracted {len(products)} products from JavaScript data in {category_name}")
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting products from JavaScript data: {e}")
            return []
    
    def _map_category(self, category_name: str) -> ProductCategory:
        """
        Map category name to ProductCategory enum
        """
        category_mapping = {
            'adhesives': ProductCategory.ADHESIVES,
            'caulk': ProductCategory.CAULK_SEALANTS,
            'sealants': ProductCategory.CAULK_SEALANTS,
            'anchoring': ProductCategory.ANCHORING_FASTENERS,
            'fasteners': ProductCategory.ANCHORING_FASTENERS,
            'brick': ProductCategory.BRICK_STONE,
            'stone': ProductCategory.BRICK_STONE,
            'building': ProductCategory.BUILDING_MATERIALS,
            'cleaning': ProductCategory.CLEANING_TOOLS,
            'concrete': ProductCategory.CONCRETE_CHEMICALS,
            'electrical': ProductCategory.ELECTRICAL_LIGHTING,
            'lighting': ProductCategory.ELECTRICAL_LIGHTING,
            'erosion': ProductCategory.EROSION_CONTROL,
            'hand': ProductCategory.HAND_TOOLS,
            'tools': ProductCategory.HAND_TOOLS,
            'jobsite': ProductCategory.JOBSITE_SUPPLIES,
            'ladders': ProductCategory.LADDERS_SCAFFOLDING,
            'scaffolding': ProductCategory.LADDERS_SCAFFOLDING,
            'masonry': ProductCategory.MASONRY_BLOCK,
            'material': ProductCategory.MATERIAL_HANDLING,
            'measuring': ProductCategory.MEASURING_MARKING,
            'power': ProductCategory.POWER_TOOLS,
            'safety': ProductCategory.SAFETY,
            'waterproofing': ProductCategory.WATERPROOFING
        }
        
        category_lower = category_name.lower()
        for key, category in category_mapping.items():
            if key in category_lower:
                return category
        
        return ProductCategory.UNKNOWN
    
    def _extract_single_product(self, element, category_name: str) -> Optional[OnlineProductData]:
        """
        Extract data from a single product element using Selenium
        
        Args:
            element: Selenium WebElement
            category_name: Name of the category
            
        Returns:
            ProductData object or None
        """
        try:
            # Extract basic product information
            product_name = self._safe_get_text(element, ".product-name, .item-name, h3, h4, .title")
            sku = self._safe_get_text(element, ".sku, .product-sku, [data-sku], .product-id")
            price_text = self._safe_get_text(element, ".price, .product-price, .item-price, .cost")
            description = self._safe_get_text(element, ".description, .product-desc, .item-desc, .summary")
            
            # Extract additional information
            mfg_number = self._safe_get_text(element, ".mfg-number, .manufacturer-number, .brand")
            availability = self._safe_get_text(element, ".availability, .stock-status, .inventory")
            
            # Get product URL
            url_element = element.find_element(By.CSS_SELECTOR, "a")
            url = url_element.get_attribute('href') if url_element else None
            
            # Parse price
            price = self._parse_price(price_text)
            
            # Determine category
            category = self.category_mapping.get(category_name, ProductCategory.UNKNOWN)
            
            # Create product data
            product_data = OnlineProductData(
                sku=sku or f"WC_{len(self.extracted_products)}",
                product_name=product_name or "Unknown Product",
                description=description or product_name or "No description available",
                size=self._extract_size(description or product_name),
                unit=self._determine_unit(description or product_name),
                price=price,
                category=category,
                subcategory=category_name,
                url=url,
                availability=availability or "unknown",
                mfg_number=mfg_number,
                construction_relevance=self._assess_construction_relevance(description or product_name, category),
                confidence_score=self._calculate_confidence_score(sku, product_name, description, price)
            )
            
            return product_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting single product: {e}")
            return None
    
    def _extract_single_product_from_soup(self, element, category_name: str) -> Optional[OnlineProductData]:
        """
        Extract data from a single product element using BeautifulSoup
        
        Args:
            element: BeautifulSoup element
            category_name: Name of the category
            
        Returns:
            ProductData object or None
        """
        try:
            # Get all text content from the element
            all_text = element.get_text(strip=True)
            
            # Extract basic product information with multiple selector strategies
            product_name = (
                self._safe_get_text_soup(element, ".product-name, .item-name, h3, h4, .title, .TypographyStyle") or
                self._safe_get_text_soup(element, "[data-test-selector*='product']") or
                self._safe_get_text_soup(element, "span, div")  # Fallback to any text
            )
            
            # Try to extract SKU from various sources
            sku = (
                self._safe_get_text_soup(element, ".sku, .product-sku, [data-sku], .product-id") or
                self._safe_get_text_soup(element, "[data-test-selector*='sku']") or
                self._extract_sku_from_text(all_text)
            )
            
            # Try to extract price from various sources
            price_text = (
                self._safe_get_text_soup(element, ".price, .product-price, .item-price, .cost") or
                self._safe_get_text_soup(element, "[data-test-selector*='price']") or
                self._extract_price_text_from_element(element)
            )
            
            # Extract description
            description = (
                self._safe_get_text_soup(element, ".description, .product-desc, .item-desc, .summary") or
                product_name or
                all_text[:200]  # Use first 200 chars as description
            )
            
            # Extract additional information
            mfg_number = self._safe_get_text_soup(element, ".mfg-number, .manufacturer-number, .brand")
            availability = self._safe_get_text_soup(element, ".availability, .stock-status, .inventory")
            
            # Get product URL
            url_element = element.find('a')
            url = urljoin(self.config.base_url, url_element.get('href')) if url_element else None
            
            # Parse price
            price = self._parse_price(price_text)
            
            # Determine category
            category = self.category_mapping.get(category_name, ProductCategory.UNKNOWN)
            
            # Only create product data if we have at least a name or description
            if not product_name and not description:
                return None
            
            # Create product data
            product_data = OnlineProductData(
                sku=sku or f"WC_{len(self.extracted_products)}",
                product_name=product_name or "Unknown Product",
                description=description or product_name or "No description available",
                size=self._extract_size(description or product_name),
                unit=self._determine_unit(description or product_name),
                price=price,
                category=category,
                subcategory=category_name,
                url=url,
                availability=availability or "unknown",
                mfg_number=mfg_number,
                construction_relevance=self._assess_construction_relevance(description or product_name, category),
                confidence_score=self._calculate_confidence_score(sku, product_name, description, price)
            )
            
            return product_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting single product: {e}")
            return None
    
    def _extract_sku_from_text(self, text: str) -> str:
        """Extract SKU from text using regex patterns"""
        if not text:
            return ""
        
        # Common SKU patterns
        sku_patterns = [
            r'SKU[:\s]*([A-Z0-9\-_]+)',
            r'Item[:\s]*([A-Z0-9\-_]+)',
            r'Product[:\s]*([A-Z0-9\-_]+)',
            r'([A-Z]{2,}[0-9]{3,})',  # Pattern like ABC123
            r'([A-Z0-9]{6,})'  # Any 6+ character alphanumeric
        ]
        
        for pattern in sku_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_price_text_from_element(self, element) -> str:
        """Extract price text from element using multiple strategies"""
        # Look for price in the element's text
        text = element.get_text()
        price_match = re.search(r'\$[\d,]+\.?\d*', text)
        if price_match:
            return price_match.group(0)
        
        # Look for price in child elements
        price_elements = element.find_all(text=re.compile(r'\$[\d,]+\.?\d*'))
        if price_elements:
            return price_elements[0].strip()
        
        return ""
    
    def _safe_get_text(self, element, selector: str) -> str:
        """Safely get text from Selenium element"""
        try:
            found_element = element.find_element(By.CSS_SELECTOR, selector)
            return found_element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _safe_get_text_soup(self, element, selector: str) -> str:
        """Safely get text from BeautifulSoup element"""
        try:
            found_element = element.select_one(selector)
            return found_element.text.strip() if found_element else ""
        except Exception:
            return ""
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text"""
        if not price_text:
            return None
        
        try:
            # Remove currency symbols and extract numeric value
            price_match = re.search(r'[\$]?([\d,]+\.?\d*)', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group(1))
        except Exception:
            pass
        
        return None
    
    def _extract_size(self, text: str) -> str:
        """Extract size information from text"""
        if not text:
            return "N/A"
        
        # Common size patterns
        size_patterns = [
            r'(\d+(?:/\d+)?["\']?x\d+(?:/\d+)?["\']?(?:x\d+(?:/\d+)?["\']?)?)',
            r'(\d+(?:/\d+)?["\']?[xX]\d+(?:/\d+)?["\']?)',
            r'(\d+(?:/\d+)?["\']?\s*[xX]\s*\d+(?:/\d+)?["\']?)',
            r'(\d+(?:/\d+)?["\']?\s*[xX]\s*\d+(?:/\d+)?["\']?\s*[xX]\s*\d+(?:/\d+)?["\']?)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "N/A"
    
    def _determine_unit(self, text: str) -> str:
        """Determine unit of measurement from text"""
        if not text:
            return "EA"
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['foot', 'feet', 'ft', "'"]):
            return "FT"
        elif any(word in text_lower for word in ['yard', 'yd']):
            return "YD"
        elif any(word in text_lower for word in ['square', 'sq', 'sf']):
            return "SF"
        elif any(word in text_lower for word in ['cubic', 'cu', 'cf']):
            return "CF"
        elif any(word in text_lower for word in ['pound', 'lb', 'lbs']):
            return "LB"
        elif any(word in text_lower for word in ['gallon', 'gal']):
            return "GAL"
        elif any(word in text_lower for word in ['piece', 'pc', 'each', 'ea']):
            return "EA"
        else:
            return "EA"
    
    def _assess_construction_relevance(self, text: str, category: ProductCategory) -> str:
        """Assess construction relevance of product"""
        if not text:
            return "low"
        
        text_lower = text.lower()
        
        # High relevance keywords
        high_relevance = {
            'concrete', 'form', 'shoring', 'rebar', 'anchor', 'fastener',
            'safety', 'harness', 'guardrail', 'hardhat', 'tool', 'equipment'
        }
        
        # Medium relevance keywords
        medium_relevance = {
            'material', 'supply', 'hardware', 'lumber', 'plywood', 'steel',
            'aluminum', 'plastic', 'adhesive', 'sealant', 'caulk'
        }
        
        if any(keyword in text_lower for keyword in high_relevance):
            return "high"
        elif any(keyword in text_lower for keyword in medium_relevance):
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence_score(self, sku: str, product_name: str, description: str, price: Optional[float]) -> float:
        """Calculate confidence score for extracted data"""
        score = 0.0
        
        if sku and sku != "N/A":
            score += 0.3
        if product_name and product_name != "Unknown Product":
            score += 0.3
        if description and description != "No description available":
            score += 0.2
        if price is not None:
            score += 0.2
        
        return min(score, 1.0)
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample product data for testing"""
        sample_products = []
        
        # Sample products from the adhesive anchor dispensing guns category
        products_data = [
            {
                "sku": "21106685",
                "product_name": "1/4\"X2\" SNAP SPIKE NYLON POWERS",
                "description": "1/4\"X2\" SNAP SPIKE NYLON POWERS",
                "size": "1/4\"X2\"",
                "unit": "EA",
                "price": 0.33,
                "category": ProductCategory.ANCHORING_FASTENERS,
                "subcategory": "Adhesive Anchor Dispensing Guns",
                "availability": "Ready to Ship",
                "mfg_number": "06685PWR"
            },
            {
                "sku": "21108286",
                "product_name": "11/16\"X7-7/8\" Epoxy Hole Cleaning Brush For 5/8\" Rebar/Rod Dewalt",
                "description": "11/16\"X7-7/8\" Epoxy Hole Cleaning Brush For 5/8\" Rebar/Rod Dewalt",
                "size": "11/16\"X7-7/8\"",
                "unit": "EA",
                "price": 30.09,
                "category": ProductCategory.ANCHORING_FASTENERS,
                "subcategory": "Adhesive Anchor Dispensing Guns",
                "availability": "Ready to Ship",
                "mfg_number": "08286PWR"
            },
            {
                "sku": "21112345",
                "product_name": "3/8\" Concrete Anchor Kit",
                "description": "3/8\" Concrete Anchor Kit with drill bit and setting tool",
                "size": "3/8\"",
                "unit": "EA",
                "price": 15.99,
                "category": ProductCategory.ANCHORING_FASTENERS,
                "subcategory": "Concrete Anchors",
                "availability": "Ready to Ship",
                "mfg_number": "CAK-38"
            },
            {
                "sku": "21123456",
                "product_name": "Safety Harness with Lanyard",
                "description": "Full body safety harness with 6ft lanyard",
                "size": "Universal",
                "unit": "EA",
                "price": 89.99,
                "category": ProductCategory.SAFETY,
                "subcategory": "Fall Protection",
                "availability": "Ready to Ship",
                "mfg_number": "SH-6FT"
            },
            {
                "sku": "21134567",
                "product_name": "Concrete Form Tie 1/2\" x 8\"",
                "description": "Heavy duty concrete form tie for construction",
                "size": "1/2\" x 8\"",
                "unit": "EA",
                "price": 0.85,
                "category": ProductCategory.CONCRETE_FORMING,
                "subcategory": "Form Ties",
                "availability": "Ready to Ship",
                "mfg_number": "CFT-12-8"
            }
        ]
        
        for product_info in products_data:
            product_data = OnlineProductData(
                sku=product_info["sku"],
                product_name=product_info["product_name"],
                description=product_info["description"],
                size=product_info["size"],
                unit=product_info["unit"],
                price=product_info["price"],
                category=product_info["category"],
                subcategory=product_info["subcategory"],
                availability=product_info["availability"],
                mfg_number=product_info["mfg_number"],
                construction_relevance=self._assess_construction_relevance(
                    product_info["description"], product_info["category"]
                ),
                confidence_score=self._calculate_confidence_score(
                    product_info["sku"], 
                    product_info["product_name"], 
                    product_info["description"], 
                    product_info["price"]
                )
            )
            sample_products.append(product_data)
        
        return pd.DataFrame([vars(product) for product in sample_products])
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the extracted DataFrame"""
        if df.empty:
            return df
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['sku', 'product_name'], keep='first')
        
        # Filter by confidence score
        if 'confidence_score' in df.columns:
            df = df[df['confidence_score'] >= self.config.min_confidence_score]
        
        # Sort by category priority and confidence
        category_priority = {
            ProductCategory.CONCRETE_FORMING.value: 1,
            ProductCategory.ANCHORING_FASTENERS.value: 2,
            ProductCategory.SAFETY.value: 3,
            ProductCategory.POWER_TOOLS.value: 4,
            ProductCategory.HAND_TOOLS.value: 5,
            ProductCategory.ADHESIVES.value: 6,
            ProductCategory.CONCRETE_CHEMICALS.value: 7,
            ProductCategory.BUILDING_MATERIALS.value: 8,
            ProductCategory.UNKNOWN.value: 9
        }
        
        df['category_priority'] = df['category'].map(category_priority).fillna(9)
        df = df.sort_values(['category_priority', 'confidence_score'], ascending=[True, False])
        df = df.drop('category_priority', axis=1)
        
        return df
    
    def export_to_csv(self, df: pd.DataFrame, output_path: Union[str, Path]) -> None:
        """Export DataFrame to CSV file"""
        output_path = Path(output_path)
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
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
def extract_whitecap_online_catalog() -> pd.DataFrame:
    """Convenience function for online catalog extraction"""
    extractor = WhitecapOnlineExtractor()
    return extractor.extract_catalog_data()


def extract_whitecap_online_categories(categories: List[str]) -> pd.DataFrame:
    """Convenience function for category-specific extraction"""
    config = OnlineExtractionConfig(categories_to_extract=categories)
    extractor = WhitecapOnlineExtractor(config)
    return extractor.extract_catalog_data()


if __name__ == "__main__":
    # Example usage
    extractor = WhitecapOnlineExtractor()
    
    try:
        # Extract all products
        df = extractor.extract_catalog_data()
        
        # Export results
        extractor.export_to_csv(df, "output/catalogs/whitecap_online_products.csv")
        
        # Print statistics
        stats = extractor.get_extraction_stats()
        print(f"Extraction completed: {stats}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        traceback.print_exc() 