# PACE - Project Analysis & Construction Estimating - Source Package

"""
PACE - Project Analysis & Construction Estimating

A comprehensive construction bidding automation platform that supports
multiple agencies including CalTrans, DOT agencies, municipalities,
federal projects, and commercial construction.

This package contains the core components for:
- Project specification analysis
- Catalog extraction and processing
- Bid generation and pricing
- Multi-agency support
- Professional reporting

For more information, visit: https://pace-construction.com
"""

__version__ = "1.0.0"
__author__ = "PACE Development Team"
__email__ = "support@pace-construction.com"
__description__ = "Project Analysis & Construction Estimating Platform"

# Import core components
from .analyzers import CalTransPDFAnalyzer, CalTransAnalysisResult
from .extractors import WhitecapCatalogExtractor
from .bidding import CalTransBiddingEngine
from .utils import ExcelBidGenerator, DataValidator, ReportGenerator

__all__ = [
    'CalTransPDFAnalyzer',
    'CalTransAnalysisResult', 
    'WhitecapCatalogExtractor',
    'CalTransBiddingEngine',
    'ExcelBidGenerator',
    'DataValidator',
    'ReportGenerator',
] 