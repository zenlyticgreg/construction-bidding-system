# PDF and Document Extractors Package for PACE - Project Analysis & Construction Estimating

"""
Extractors Package for PACE

This package contains extractors for various document types used in
construction bidding, including catalog PDFs and project specifications.

Components:
- WhitecapCatalogExtractor: Extracts product data from Whitecap catalogs
- Future extractors for other catalog formats and document types
"""

from .whitecap_extractor import WhitecapCatalogExtractor, extract_whitecap_catalog, extract_whitecap_sections

__all__ = [
    'WhitecapCatalogExtractor',
    'extract_whitecap_catalog',
    'extract_whitecap_sections',
] 