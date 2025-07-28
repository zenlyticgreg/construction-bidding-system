"""
Product Matcher for PACE - Project Analysis & Construction Estimating

This module provides intelligent product matching capabilities for the PACE
construction bidding automation platform, supporting multiple agencies and
catalog formats.

The matcher supports:
- Multi-agency terminology matching
- Fuzzy string matching algorithms
- Product categorization and classification
- Confidence scoring and ranking
- Cross-reference validation
- Custom matching rules and preferences

For more information, visit: https://pace-construction.com
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    # Fallback fuzzy matching functions
    def simple_fuzzy_ratio(s1, s2):
        """Simple fallback fuzzy ratio calculation"""
        if not s1 or not s2:
            return 0
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        if s1_lower == s2_lower:
            return 100
        if s1_lower in s2_lower or s2_lower in s1_lower:
            return 80
        return 50
    
    def simple_partial_ratio(s1, s2):
        """Simple fallback partial ratio calculation"""
        return simple_fuzzy_ratio(s1, s2)
    
    fuzz = type('Fuzz', (), {
        'ratio': simple_fuzzy_ratio,
        'partial_ratio': simple_partial_ratio
    })()
    
    def process_extract(query, choices, limit=3, scorer=None):
        """Simple fallback process.extract"""
        if scorer is None:
            scorer = simple_fuzzy_ratio
        
        results = []
        for choice in choices:
            score = scorer(query, choice)
            results.append((choice, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    process = type('Process', (), {
        'extract': process_extract
    })()

# Local imports
try:
    from config.settings import get_setting
except ImportError:
    # Fallback for testing without full project structure
    def get_setting(key: str, default: Any = None) -> Any:
        """Fallback settings function for testing"""
        return default


class ProductCategory(Enum):
    """Product categories for pricing and matching"""
    FORMWORK = "formwork"
    LUMBER = "lumber"
    HARDWARE = "hardware"
    TOOLS = "tools"
    SAFETY = "safety"
    CONCRETE = "concrete"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    PAINT = "paint"
    FASTENERS = "fasteners"
    OTHER = "other"


class MatchQuality(Enum):
    """Match quality levels"""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    POOR = "poor"


@dataclass
class ProductMatch:
    """Represents a matched product with scoring and metadata"""
    product_id: str
    product_name: str
    category: str
    match_score: float
    quality: MatchQuality
    price: Optional[float] = None
    estimated_price: Optional[float] = None
    supplier: str = "Whitecap"
    availability: bool = True
    alternatives: List[str] = field(default_factory=list)
    match_reason: str = ""
    confidence: float = 1.0


@dataclass
class PricingTier:
    """Pricing tier configuration"""
    base_price: float
    size_multipliers: Dict[str, float]
    quality_adjustments: Dict[str, float]
    category_weights: Dict[str, float]


class ProductMatcher:
    """
    Intelligent product matcher for CalTrans bidding system.
    
    Features:
    - Smart matching between CalTrans terms and Whitecap products
    - Fuzzy string matching with configurable thresholds
    - Construction-relevant product prioritization
    - Pricing estimation for missing prices
    - Alternative product suggestions
    - Multi-criteria scoring system
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the ProductMatcher with configuration and logging."""
        self.logger = logger or self._setup_logger()
        
        # Initialize pricing tiers
        self.pricing_tiers = self._initialize_pricing_tiers()
        
        # Construction-relevant keywords for prioritization
        self.construction_keywords = {
            "formwork", "lumber", "plywood", "concrete", "rebar", "steel",
            "fasteners", "nails", "screws", "bolts", "hardware", "tools",
            "safety", "equipment", "materials", "supplies", "construction"
        }
        
        # Category-specific matching weights
        self.category_weights = {
            ProductCategory.FORMWORK: 1.0,
            ProductCategory.LUMBER: 0.95,
            ProductCategory.HARDWARE: 0.9,
            ProductCategory.TOOLS: 0.85,
            ProductCategory.SAFETY: 0.8,
            ProductCategory.CONCRETE: 0.9,
            ProductCategory.ELECTRICAL: 0.7,
            ProductCategory.PLUMBING: 0.7,
            ProductCategory.PAINT: 0.6,
            ProductCategory.FASTENERS: 0.85,
            ProductCategory.OTHER: 0.5
        }
        
        # Fuzzy matching thresholds
        self.match_thresholds = {
            MatchQuality.EXACT: 100,
            MatchQuality.HIGH: 85,
            MatchQuality.MEDIUM: 70,
            MatchQuality.LOW: 50,
            MatchQuality.POOR: 30
        }
        
        # Sample product database (in real implementation, this would be loaded from Whitecap catalog)
        self.product_database = self._initialize_sample_products()
        
        self.logger.info("ProductMatcher initialized successfully")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the ProductMatcher."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_pricing_tiers(self) -> Dict[str, PricingTier]:
        """Initialize pricing tiers for different product categories."""
        return {
            ProductCategory.FORMWORK.value: PricingTier(
                base_price=3.50,
                size_multipliers={
                    "4x8": 1.0,
                    "4x10": 1.25,
                    "5x10": 1.5,
                    "custom": 1.2
                },
                quality_adjustments={
                    "standard": 1.0,
                    "marine": 1.3,
                    "fire_rated": 1.4,
                    "moisture_resistant": 1.2
                },
                category_weights={"formwork": 1.0, "lumber": 0.8}
            ),
            ProductCategory.LUMBER.value: PricingTier(
                base_price=1.25,
                size_multipliers={
                    "2x4": 1.0,
                    "2x6": 1.4,
                    "2x8": 1.8,
                    "2x10": 2.2,
                    "2x12": 2.6,
                    "4x4": 2.0,
                    "6x6": 4.0
                },
                quality_adjustments={
                    "standard": 1.0,
                    "pressure_treated": 1.3,
                    "cedar": 1.5,
                    "redwood": 1.8,
                    "douglas_fir": 1.2
                },
                category_weights={"lumber": 1.0, "formwork": 0.9}
            ),
            ProductCategory.HARDWARE.value: PricingTier(
                base_price=2.00,
                size_multipliers={
                    "small": 0.8,
                    "medium": 1.0,
                    "large": 1.3,
                    "heavy": 1.6
                },
                quality_adjustments={
                    "standard": 1.0,
                    "galvanized": 1.2,
                    "stainless": 1.5,
                    "zinc_plated": 1.1
                },
                category_weights={"hardware": 1.0, "fasteners": 0.9}
            ),
            ProductCategory.TOOLS.value: PricingTier(
                base_price=15.00,
                size_multipliers={
                    "hand": 0.7,
                    "power": 1.0,
                    "heavy_duty": 1.4,
                    "professional": 1.8
                },
                quality_adjustments={
                    "standard": 1.0,
                    "premium": 1.3,
                    "professional": 1.6,
                    "industrial": 2.0
                },
                category_weights={"tools": 1.0, "equipment": 0.9}
            ),
            ProductCategory.SAFETY.value: PricingTier(
                base_price=8.00,
                size_multipliers={
                    "basic": 0.8,
                    "standard": 1.0,
                    "premium": 1.3,
                    "specialty": 1.6
                },
                quality_adjustments={
                    "standard": 1.0,
                    "ansi_rated": 1.2,
                    "osha_compliant": 1.3,
                    "premium": 1.4
                },
                category_weights={"safety": 1.0, "ppe": 0.9}
            )
        }
    
    def _initialize_sample_products(self) -> Dict[str, Dict[str, Any]]:
        """Initialize sample product database for demonstration."""
        return {
            "FW001": {
                "name": "3/4\" CDX Plywood 4x8",
                "category": ProductCategory.FORMWORK.value,
                "price": 32.50,
                "keywords": ["plywood", "formwork", "cdx", "3/4", "4x8"],
                "specifications": {"thickness": "3/4\"", "size": "4x8", "grade": "CDX"}
            },
            "FW002": {
                "name": "1\" CDX Plywood 4x8",
                "category": ProductCategory.FORMWORK.value,
                "price": 42.00,
                "keywords": ["plywood", "formwork", "cdx", "1\"", "4x8"],
                "specifications": {"thickness": "1\"", "size": "4x8", "grade": "CDX"}
            },
            "LB001": {
                "name": "2x4x8 Douglas Fir",
                "category": ProductCategory.LUMBER.value,
                "price": 8.50,
                "keywords": ["lumber", "2x4", "douglas", "fir", "8ft"],
                "specifications": {"size": "2x4", "length": "8ft", "species": "Douglas Fir"}
            },
            "LB002": {
                "name": "2x6x10 Douglas Fir",
                "category": ProductCategory.LUMBER.value,
                "price": 15.75,
                "keywords": ["lumber", "2x6", "douglas", "fir", "10ft"],
                "specifications": {"size": "2x6", "length": "10ft", "species": "Douglas Fir"}
            },
            "HW001": {
                "name": "3/8\" x 3\" Carriage Bolt",
                "category": ProductCategory.HARDWARE.value,
                "price": 2.25,
                "keywords": ["bolt", "carriage", "3/8", "hardware"],
                "specifications": {"diameter": "3/8\"", "length": "3\"", "type": "carriage"}
            },
            "HW002": {
                "name": "1/2\" x 4\" Lag Screw",
                "category": ProductCategory.HARDWARE.value,
                "price": 3.50,
                "keywords": ["screw", "lag", "1/2", "hardware"],
                "specifications": {"diameter": "1/2\"", "length": "4\"", "type": "lag"}
            },
            "TL001": {
                "name": "20oz Framing Hammer",
                "category": ProductCategory.TOOLS.value,
                "price": 28.00,
                "keywords": ["hammer", "framing", "20oz", "tool"],
                "specifications": {"weight": "20oz", "type": "framing"}
            },
            "SF001": {
                "name": "Hard Hat Class E",
                "category": ProductCategory.SAFETY.value,
                "price": 12.50,
                "keywords": ["hard hat", "safety", "class e", "helmet"],
                "specifications": {"class": "E", "type": "hard hat"}
            }
        }
    
    def find_products_by_terms(
        self, 
        search_terms: List[str], 
        lumber_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find products matching the given search terms.
        
        Args:
            search_terms: List of terms to search for
            lumber_category: Optional lumber category filter
            
        Returns:
            List of matched products with scores and metadata
        """
        self.logger.info(f"Searching for products with terms: {search_terms}")
        
        matches = []
        search_text = " ".join(search_terms).lower()
        
        for product_id, product_data in self.product_database.items():
            # Skip if lumber category filter is applied and doesn't match
            if lumber_category and product_data["category"] != lumber_category:
                continue
            
            # Calculate match score
            match_score = self.score_product_match(product_data, search_terms)
            
            if match_score > 0:
                # Determine match quality
                quality = self._determine_match_quality(match_score)
                
                # Estimate price if not available
                estimated_price = None
                if not product_data.get("price"):
                    estimated_price = self.estimate_price_for_product(product_data)
                
                # Create product match
                product_match = ProductMatch(
                    product_id=product_id,
                    product_name=product_data["name"],
                    category=product_data["category"],
                    match_score=match_score,
                    quality=quality,
                    price=product_data.get("price"),
                    estimated_price=estimated_price,
                    match_reason=self._generate_match_reason(product_data, search_terms, match_score)
                )
                
                matches.append(product_match)
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Convert to dictionaries for return
        result = []
        for match in matches:
            result.append({
                "product_id": match.product_id,
                "product_name": match.product_name,
                "category": match.category,
                "match_score": match.match_score,
                "quality": match.quality.value,
                "price": match.price,
                "estimated_price": match.estimated_price,
                "supplier": match.supplier,
                "availability": match.availability,
                "match_reason": match.match_reason,
                "confidence": match.confidence
            })
        
        self.logger.info(f"Found {len(result)} product matches")
        return result
    
    def find_best_match(
        self, 
        search_term: str, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find the best single match for a search term.
        
        Args:
            search_term: Term to search for
            category: Optional category filter
            
        Returns:
            List containing the best match(es)
        """
        self.logger.info(f"Finding best match for: {search_term}")
        
        # Use fuzzy matching to find the best product name match
        product_names = [
            (pid, pdata["name"]) 
            for pid, pdata in self.product_database.items()
            if not category or pdata["category"] == category
        ]
        
        if not product_names:
            return []
        
        # Use fuzzywuzzy process to find best matches
        matches = process.extract(
            search_term, 
            [name for _, name in product_names],
            limit=3,
            scorer=fuzz.token_sort_ratio
        )
        
        best_matches = []
        for match_name, score in matches:
            if score >= self.match_thresholds[MatchQuality.MEDIUM]:
                # Find the product ID for this name
                product_id = next(pid for pid, name in product_names if name == match_name)
                product_data = self.product_database[product_id]
                
                # Create detailed match
                product_match = ProductMatch(
                    product_id=product_id,
                    product_name=product_data["name"],
                    category=product_data["category"],
                    match_score=score,
                    quality=self._determine_match_quality(score),
                    price=product_data.get("price"),
                    estimated_price=self.estimate_price_for_product(product_data) if not product_data.get("price") else None,
                    match_reason=f"Best fuzzy match for '{search_term}' (score: {score})"
                )
                
                best_matches.append({
                    "product_id": product_match.product_id,
                    "product_name": product_match.product_name,
                    "category": product_match.category,
                    "match_score": product_match.match_score,
                    "quality": product_match.quality.value,
                    "price": product_match.price,
                    "estimated_price": product_match.estimated_price,
                    "supplier": product_match.supplier,
                    "availability": product_match.availability,
                    "match_reason": product_match.match_reason,
                    "confidence": product_match.confidence
                })
        
        self.logger.info(f"Found {len(best_matches)} best matches")
        return best_matches
    
    def estimate_prices(self) -> Union[pd.Series, Dict[str, float]]:
        """
        Estimate prices for all products in the database.
        
        Returns:
            Pandas Series with product IDs and estimated prices, or dict if pandas unavailable
        """
        self.logger.info("Estimating prices for all products")
        
        estimated_prices = {}
        for product_id, product_data in self.product_database.items():
            if not product_data.get("price"):
                estimated_price = self.estimate_price_for_product(product_data)
                estimated_prices[product_id] = estimated_price
        
        if PANDAS_AVAILABLE and pd is not None:
            return pd.Series(estimated_prices)
        else:
            return estimated_prices
    
    def score_product_match(
        self, 
        product: Dict[str, Any], 
        search_terms: List[str]
    ) -> float:
        """
        Score a product match based on multiple criteria.
        
        Args:
            product: Product data dictionary
            search_terms: List of search terms
            
        Returns:
            Match score between 0 and 100
        """
        if not search_terms:
            return 0.0
        
        total_score = 0.0
        max_possible_score = 0.0
        
        # 1. Name matching (40% weight)
        name_score = self._calculate_name_match_score(product["name"], search_terms)
        total_score += name_score * 0.4
        max_possible_score += 100 * 0.4
        
        # 2. Keyword matching (30% weight)
        keyword_score = self._calculate_keyword_match_score(product.get("keywords", []), search_terms)
        total_score += keyword_score * 0.3
        max_possible_score += 100 * 0.3
        
        # 3. Category relevance (20% weight)
        category_score = self._calculate_category_relevance_score(product["category"], search_terms)
        total_score += category_score * 0.2
        max_possible_score += 100 * 0.2
        
        # 4. Construction relevance bonus (10% weight)
        construction_score = self._calculate_construction_relevance_score(product, search_terms)
        total_score += construction_score * 0.1
        max_possible_score += 100 * 0.1
        
        # Normalize to 0-100 scale
        if max_possible_score > 0:
            final_score = (total_score / max_possible_score) * 100
        else:
            final_score = 0.0
        
        return min(100.0, max(0.0, final_score))
    
    def estimate_price_for_product(self, product: Dict[str, Any]) -> Optional[float]:
        """
        Estimate price for a specific product.
        
        Args:
            product: Product data dictionary
            
        Returns:
            Estimated price or None if cannot estimate
        """
        category = product["category"]
        if category not in self.pricing_tiers:
            return None
        
        pricing_tier = self.pricing_tiers[category]
        base_price = pricing_tier.base_price
        
        # Apply size multiplier
        size_multiplier = 1.0
        product_name = product["name"].lower()
        for size, multiplier in pricing_tier.size_multipliers.items():
            if size in product_name:
                size_multiplier = multiplier
                break
        
        # Apply quality adjustment
        quality_multiplier = 1.0
        for quality, adjustment in pricing_tier.quality_adjustments.items():
            if quality in product_name:
                quality_multiplier = adjustment
                break
        
        # Apply category-specific adjustments
        category_weight = pricing_tier.category_weights.get(category, 1.0)
        
        estimated_price = base_price * size_multiplier * quality_multiplier * category_weight
        
        # Round to 2 decimal places
        return round(estimated_price, 2)
    
    def _calculate_name_match_score(self, product_name: str, search_terms: List[str]) -> float:
        """Calculate name matching score."""
        if not search_terms:
            return 0.0
        
        product_name_lower = product_name.lower()
        max_score = 0.0
        
        for term in search_terms:
            term_lower = term.lower()
            
            # Exact match gets highest score
            if term_lower in product_name_lower:
                score = 100.0
            else:
                # Use fuzzy matching
                score = fuzz.partial_ratio(term_lower, product_name_lower)
            
            max_score = max(max_score, score)
        
        return max_score
    
    def _calculate_keyword_match_score(self, product_keywords: List[str], search_terms: List[str]) -> float:
        """Calculate keyword matching score."""
        if not product_keywords or not search_terms:
            return 0.0
        
        matches = 0
        total_terms = len(search_terms)
        
        for term in search_terms:
            term_lower = term.lower()
            for keyword in product_keywords:
                keyword_lower = keyword.lower()
                
                # Check for exact or partial matches
                if (term_lower in keyword_lower or 
                    keyword_lower in term_lower or 
                    fuzz.partial_ratio(term_lower, keyword_lower) > 80):
                    matches += 1
                    break
        
        return (matches / total_terms) * 100 if total_terms > 0 else 0.0
    
    def _calculate_category_relevance_score(self, product_category: str, search_terms: List[str]) -> float:
        """Calculate category relevance score."""
        if not search_terms:
            return 0.0
        
        # Check if any search terms are construction-related
        construction_terms = sum(1 for term in search_terms if term.lower() in self.construction_keywords)
        
        if construction_terms > 0:
            # Higher score for construction-relevant categories
            construction_categories = {
                ProductCategory.FORMWORK.value,
                ProductCategory.LUMBER.value,
                ProductCategory.HARDWARE.value,
                ProductCategory.TOOLS.value,
                ProductCategory.SAFETY.value
            }
            
            if product_category in construction_categories:
                return 100.0
            else:
                return 60.0
        else:
            # For non-construction terms, all categories are equally relevant
            return 80.0
    
    def _calculate_construction_relevance_score(self, product: Dict[str, Any], search_terms: List[str]) -> float:
        """Calculate construction relevance bonus score."""
        product_name = product["name"].lower()
        product_keywords = [kw.lower() for kw in product.get("keywords", [])]
        
        # Check for construction-specific terms in product
        construction_indicators = 0
        
        for term in self.construction_keywords:
            if (term in product_name or 
                any(term in kw for kw in product_keywords)):
                construction_indicators += 1
        
        # Bonus score based on construction relevance
        if construction_indicators >= 2:
            return 100.0
        elif construction_indicators == 1:
            return 70.0
        else:
            return 30.0
    
    def _determine_match_quality(self, score: float) -> MatchQuality:
        """Determine match quality based on score."""
        if score >= self.match_thresholds[MatchQuality.EXACT]:
            return MatchQuality.EXACT
        elif score >= self.match_thresholds[MatchQuality.HIGH]:
            return MatchQuality.HIGH
        elif score >= self.match_thresholds[MatchQuality.MEDIUM]:
            return MatchQuality.MEDIUM
        elif score >= self.match_thresholds[MatchQuality.LOW]:
            return MatchQuality.LOW
        else:
            return MatchQuality.POOR
    
    def _generate_match_reason(
        self, 
        product: Dict[str, Any], 
        search_terms: List[str], 
        score: float
    ) -> str:
        """Generate human-readable match reason."""
        reasons = []
        
        product_name = product["name"].lower()
        search_text = " ".join(search_terms).lower()
        
        # Check for exact matches
        for term in search_terms:
            if term.lower() in product_name:
                reasons.append(f"Exact match for '{term}'")
        
        # Check for keyword matches
        keyword_matches = []
        for term in search_terms:
            for keyword in product.get("keywords", []):
                if term.lower() in keyword.lower():
                    keyword_matches.append(f"'{term}' matches keyword '{keyword}'")
        
        if keyword_matches:
            reasons.extend(keyword_matches[:2])  # Limit to 2 keyword matches
        
        # Add category relevance
        if product["category"] in [cat.value for cat in [ProductCategory.FORMWORK, ProductCategory.LUMBER, ProductCategory.HARDWARE]]:
            reasons.append("Construction-relevant category")
        
        # Add score information
        if reasons:
            return f"{'; '.join(reasons)} (score: {score:.1f})"
        else:
            return f"Fuzzy match (score: {score:.1f})"
    
    def get_alternative_suggestions(
        self, 
        product_id: str, 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get alternative product suggestions for a given product.
        
        Args:
            product_id: ID of the product to find alternatives for
            limit: Maximum number of alternatives to return
            
        Returns:
            List of alternative products
        """
        if product_id not in self.product_database:
            return []
        
        target_product = self.product_database[product_id]
        alternatives = []
        
        for pid, product_data in self.product_database.items():
            if pid == product_id:
                continue
            
            # Score similarity to target product
            similarity_score = fuzz.token_sort_ratio(
                target_product["name"], 
                product_data["name"]
            )
            
            if similarity_score > 50:  # Only include reasonably similar products
                alternatives.append({
                    "product_id": pid,
                    "product_name": product_data["name"],
                    "category": product_data["category"],
                    "similarity_score": similarity_score,
                    "price": product_data.get("price"),
                    "estimated_price": self.estimate_price_for_product(product_data) if not product_data.get("price") else None
                })
        
        # Sort by similarity score and return top matches
        alternatives.sort(key=lambda x: x["similarity_score"], reverse=True)
        return alternatives[:limit]


def create_product_matcher() -> ProductMatcher:
    """Factory function to create a ProductMatcher instance."""
    return ProductMatcher()


# Example usage and testing functions
def test_product_matcher():
    """Test the ProductMatcher functionality."""
    matcher = ProductMatcher()
    
    # Test basic search
    results = matcher.find_products_by_terms(["plywood", "formwork"])
    print(f"Found {len(results)} matches for 'plywood formwork'")
    
    # Test best match
    best_matches = matcher.find_best_match("2x4 lumber")
    print(f"Best matches for '2x4 lumber': {len(best_matches)}")
    
    # Test price estimation
    estimated_prices = matcher.estimate_prices()
    print(f"Estimated prices for {len(estimated_prices)} products")
    
    return matcher


if __name__ == "__main__":
    test_product_matcher() 