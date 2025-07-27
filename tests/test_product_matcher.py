"""
Tests for ProductMatcher class
"""

import unittest
from unittest.mock import Mock
import pandas as pd

# Import the ProductMatcher class
try:
    from src.analyzers.product_matcher import (
        ProductMatcher, 
        ProductMatch, 
        ProductCategory, 
        MatchQuality
    )
except ImportError:
    # Fallback for testing without full project structure
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from analyzers.product_matcher import (
        ProductMatcher, 
        ProductMatch, 
        ProductCategory, 
        MatchQuality
    )


class TestProductMatcher(unittest.TestCase):
    """Test cases for ProductMatcher class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matcher = ProductMatcher()
    
    def test_initialization(self):
        """Test ProductMatcher initialization"""
        self.assertIsNotNone(self.matcher)
        self.assertIsNotNone(self.matcher.pricing_tiers)
        self.assertIsNotNone(self.matcher.product_database)
        self.assertIsNotNone(self.matcher.construction_keywords)
    
    def test_find_products_by_terms(self):
        """Test finding products by search terms"""
        results = self.matcher.find_products_by_terms(["plywood", "formwork"])
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check that results have expected structure
        for result in results:
            self.assertIn("product_id", result)
            self.assertIn("product_name", result)
            self.assertIn("match_score", result)
            self.assertIn("quality", result)
            self.assertIsInstance(result["match_score"], (int, float))
    
    def test_find_best_match(self):
        """Test finding best match for a single term"""
        results = self.matcher.find_best_match("2x4 lumber")
        
        self.assertIsInstance(results, list)
        if results:  # If any matches found
            self.assertIn("product_id", results[0])
            self.assertIn("product_name", results[0])
            self.assertIn("match_score", results[0])
    
    def test_score_product_match(self):
        """Test product match scoring"""
        # Test with a sample product
        product = {
            "name": "3/4\" CDX Plywood 4x8",
            "category": "formwork",
            "keywords": ["plywood", "formwork", "cdx", "3/4", "4x8"]
        }
        
        search_terms = ["plywood", "formwork"]
        score = self.matcher.score_product_match(product, search_terms)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_estimate_price_for_product(self):
        """Test price estimation"""
        product = {
            "name": "2x4x8 Douglas Fir",
            "category": "lumber",
            "keywords": ["lumber", "2x4", "douglas", "fir", "8ft"]
        }
        
        estimated_price = self.matcher.estimate_price_for_product(product)
        
        self.assertIsNotNone(estimated_price)
        self.assertIsInstance(estimated_price, float)
        self.assertGreater(estimated_price, 0.0)
    
    def test_estimate_prices(self):
        """Test bulk price estimation"""
        estimated_prices = self.matcher.estimate_prices()
        
        self.assertIsInstance(estimated_prices, pd.Series)
        self.assertGreater(len(estimated_prices), 0)
    
    def test_determine_match_quality(self):
        """Test match quality determination"""
        # Test exact match
        quality = self.matcher._determine_match_quality(100)
        self.assertEqual(quality, MatchQuality.EXACT)
        
        # Test high match
        quality = self.matcher._determine_match_quality(90)
        self.assertEqual(quality, MatchQuality.HIGH)
        
        # Test medium match
        quality = self.matcher._determine_match_quality(75)
        self.assertEqual(quality, MatchQuality.MEDIUM)
        
        # Test low match
        quality = self.matcher._determine_match_quality(60)
        self.assertEqual(quality, MatchQuality.LOW)
        
        # Test poor match
        quality = self.matcher._determine_match_quality(25)
        self.assertEqual(quality, MatchQuality.POOR)
    
    def test_get_alternative_suggestions(self):
        """Test alternative product suggestions"""
        # Use the first product in the database
        if self.matcher.product_database:
            first_product_id = list(self.matcher.product_database.keys())[0]
            alternatives = self.matcher.get_alternative_suggestions(first_product_id, limit=2)
            
            self.assertIsInstance(alternatives, list)
            self.assertLessEqual(len(alternatives), 2)
            
            if alternatives:
                self.assertIn("product_id", alternatives[0])
                self.assertIn("similarity_score", alternatives[0])
    
    def test_construction_keywords_prioritization(self):
        """Test that construction keywords are properly prioritized"""
        # Test with construction terms
        construction_results = self.matcher.find_products_by_terms(["formwork", "lumber"])
        
        # Test with non-construction terms
        non_construction_results = self.matcher.find_products_by_terms(["office", "supplies"])
        
        # Construction terms should generally have higher scores
        if construction_results and non_construction_results:
            avg_construction_score = sum(r["match_score"] for r in construction_results) / len(construction_results)
            avg_non_construction_score = sum(r["match_score"] for r in non_construction_results) / len(non_construction_results)
            
            # Construction terms should have higher average scores
            self.assertGreaterEqual(avg_construction_score, avg_non_construction_score)
    
    def test_category_filtering(self):
        """Test category-based filtering"""
        # Test with lumber category filter
        lumber_results = self.matcher.find_products_by_terms(["wood"], lumber_category="lumber")
        
        # All results should be in lumber category
        for result in lumber_results:
            self.assertEqual(result["category"], "lumber")
    
    def test_empty_search_terms(self):
        """Test behavior with empty search terms"""
        results = self.matcher.find_products_by_terms([])
        self.assertEqual(len(results), 0)
        
        score = self.matcher.score_product_match({"name": "test", "category": "test"}, [])
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main() 