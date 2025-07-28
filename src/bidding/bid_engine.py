"""
CalTrans Bidding Engine

This module provides a comprehensive bidding engine that combines CalTrans PDF analysis
with Whitecap product matching to generate complete bid packages with line items,
pricing calculations, and project-specific configurations.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json

# Local imports
try:
    from analyzers.caltrans_analyzer import CalTransPDFAnalyzer, CalTransAnalysisResult, TermMatch, ExtractedQuantity, ComprehensiveAnalysisResult, BidLineItem as AnalyzerBidLineItem
    from analyzers.product_matcher import ProductMatcher, ProductMatch
except ImportError:
    # Fallback for testing without full project structure
    CalTransPDFAnalyzer = None
    CalTransAnalysisResult = None
    TermMatch = None
    ExtractedQuantity = None
    ComprehensiveAnalysisResult = None
    AnalyzerBidLineItem = None
    ProductMatcher = None
    ProductMatch = None


class WasteFactor(Enum):
    """Waste factors for different material categories"""
    FORMWORK = 0.10  # 10%
    LUMBER = 0.10    # 10%
    HARDWARE = 0.05  # 5%
    SPECIALTY = 0.15 # 15%
    DEFAULT = 0.08   # 8%


class PricingConfig:
    """Configuration for pricing calculations"""
    DEFAULT_MARKUP = 0.20  # 20%
    DELIVERY_PERCENTAGE = 0.03  # 3%
    DELIVERY_MINIMUM = 150.00  # $150 minimum
    WASTE_FACTORS = {
        "formwork": WasteFactor.FORMWORK.value,
        "lumber": WasteFactor.LUMBER.value,
        "hardware": WasteFactor.HARDWARE.value,
        "specialty": WasteFactor.SPECIALTY.value,
        "default": WasteFactor.DEFAULT.value
    }


@dataclass
class BidLineItem:
    """Represents a single line item in a bid"""
    item_number: str
    description: str
    caltrans_term: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    product_matches: List[Dict[str, Any]] = field(default_factory=list)
    waste_factor: float = 0.08
    markup_percentage: float = 0.20
    delivery_fee: float = 0.0
    notes: str = ""
    confidence: float = 1.0
    source_documents: List[str] = field(default_factory=list)
    cross_references: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PricingSummary:
    """Summary of bid pricing calculations"""
    subtotal: float = 0.0
    markup_amount: float = 0.0
    delivery_fee: float = 0.0
    waste_adjustments: float = 0.0
    total: float = 0.0
    line_item_count: int = 0
    high_priority_items: int = 0
    estimated_materials_cost: float = 0.0
    estimated_labor_cost: float = 0.0


@dataclass
class BidPackage:
    """Complete bid package with all components"""
    project_name: str
    project_number: str
    bid_date: datetime = field(default_factory=datetime.now)
    line_items: List[BidLineItem] = field(default_factory=list)
    pricing_summary: PricingSummary = field(default_factory=PricingSummary)
    analysis_results: Optional[CalTransAnalysisResult] = None
    comprehensive_results: Optional[ComprehensiveAnalysisResult] = None
    markup_percentage: float = 0.20
    delivery_fee: float = 0.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidenceReport:
    """Confidence report for bid generation"""
    overall_confidence: float = 0.0
    document_coverage: Dict[str, float] = field(default_factory=dict)
    quantity_confidence: Dict[str, float] = field(default_factory=dict)
    product_match_confidence: Dict[str, float] = field(default_factory=dict)
    cross_reference_validation: Dict[str, Any] = field(default_factory=dict)
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    manual_review_items: List[str] = field(default_factory=list)


class CalTransBiddingEngine:
    """
    Comprehensive bidding engine for CalTrans projects.
    
    Features:
    - Combines CalTrans analysis with Whitecap product matching
    - Generates complete bid packages with line items
    - Applies markup, delivery fees, and waste factors
    - Calculates quantities based on CalTrans terminology
    - Provides bid summary with pricing breakdown
    - Handles project-specific configurations
    - Supports multi-file comprehensive analysis
    - Processes official bid forms with cross-referencing
    - Generates confidence reports and validation
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the bidding engine"""
        self.logger = logger or self._setup_logger()
        
        # Initialize analyzers
        self.caltrans_analyzer = CalTransPDFAnalyzer(logger) if CalTransPDFAnalyzer else None
        self.product_matcher = ProductMatcher(logger) if ProductMatcher else None
        
        # Product matching strategies for different CalTrans terms
        self.matching_strategies = {
            "BALUSTER": ["concrete", "form", "heavy", "plywood", "CDX"],
            "BLOCKOUT": ["lumber", "2x4", "2x6", "construction", "grade"],
            "STAMPED_CONCRETE": ["texture", "form", "liner", "pattern"],
            "RETAINING_WALL": ["form", "tie", "plywood", "wall"],
            "EROSION_CONTROL": ["post", "stake", "treated", "fence"],
            "FORMWORK": ["plywood", "form", "CDX", "sheathing"],
            "FALSEWORK": ["lumber", "support", "temporary", "structure"],
            "BRIDGE_RAILING": ["steel", "rail", "post", "hardware"],
            "CONCRETE_FINISHING": ["tool", "finish", "texture", "pattern"],
            "TEMPORARY_STRUCTURES": ["lumber", "plywood", "hardware", "support"]
        }
        
        # Quantity calculation factors
        self.quantity_factors = {
            "BALUSTER": {"base_factor": 1.0, "unit": "EA"},
            "BLOCKOUT": {"base_factor": 1.0, "unit": "EA"},
            "STAMPED_CONCRETE": {"base_factor": 1.0, "unit": "SQFT"},
            "RETAINING_WALL": {"base_factor": 1.0, "unit": "SQFT"},
            "EROSION_CONTROL": {"base_factor": 1.0, "unit": "LF"},
            "FORMWORK": {"base_factor": 1.0, "unit": "SQFT"},
            "FALSEWORK": {"base_factor": 1.0, "unit": "SQFT"},
            "BRIDGE_RAILING": {"base_factor": 1.0, "unit": "LF"},
            "CONCRETE_FINISHING": {"base_factor": 1.0, "unit": "SQFT"},
            "TEMPORARY_STRUCTURES": {"base_factor": 1.0, "unit": "EA"}
        }
        
        # Document context mapping for enhanced product matching
        self.document_context_mapping = {
            "specifications": {
                "focus": "material_requirements",
                "priority_terms": ["BALUSTER", "FORMWORK", "CONCRETE", "LUMBER"],
                "confidence_boost": 1.2
            },
            "bid_forms": {
                "focus": "official_quantities",
                "priority_terms": ["ITEM_NUMBER", "DESCRIPTION", "QUANTITY", "UNIT_PRICE"],
                "confidence_boost": 1.5
            },
            "construction_plans": {
                "focus": "dimensional_validation",
                "priority_terms": ["DIMENSIONS", "ELEVATIONS", "SECTIONS", "DETAILS"],
                "confidence_boost": 1.1
            },
            "supplemental": {
                "focus": "special_requirements",
                "priority_terms": ["SPECIAL", "CUSTOM", "ALTERNATIVE", "SUBSTITUTION"],
                "confidence_boost": 1.3
            }
        }
        
        self.logger.info("CalTransBiddingEngine initialized successfully")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the bidding engine"""
        logger = logging.getLogger("caltrans_bidding_engine")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def generate_complete_bid(
        self, 
        project_files_dict: Dict[str, str], 
        project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ENHANCED METHOD: Generate complete bid from multiple project files with comprehensive analysis.
        
        Args:
            project_files_dict: Dictionary mapping document types to file paths
                {"specifications": path, "bid_forms": path, "plans": path, "supplemental": path}
            project_details: Dictionary containing project information
                {"name": str, "number": str, "markup_percentage": float, etc.}
            
        Returns:
            Dictionary containing the complete bid package with source attribution
        """
        self.logger.info(f"Generating comprehensive bid for project: {project_details.get('name', 'Unknown')}")
        
        try:
            # Step 1: Perform comprehensive multi-file analysis
            if not self.caltrans_analyzer:
                raise RuntimeError("CalTrans analyzer not available")
            
            comprehensive_analysis = self.caltrans_analyzer.analyze_multiple_files(project_files_dict)
            self.logger.info(f"Comprehensive analysis completed: {comprehensive_analysis.total_terms} terms found across {comprehensive_analysis.total_documents} documents")
            
            # Step 2: Process official bid items from bid forms
            official_bid_items = self.process_official_bid_items(comprehensive_analysis)
            self.logger.info(f"Processed {len(official_bid_items)} official bid items")
            
            # Step 3: Create bid package with comprehensive results
            bid_package = BidPackage(
                project_name=project_details.get('name', 'Unknown Project'),
                project_number=project_details.get('number', 'Unknown'),
                markup_percentage=project_details.get('markup_percentage', 0.20),
                comprehensive_results=comprehensive_analysis
            )
            
            # Step 4: Generate line items with enhanced product matching
            line_items = self._generate_line_items_with_context(
                comprehensive_analysis, 
                official_bid_items,
                project_files_dict
            )
            bid_package.line_items = line_items
            
            # Step 5: Calculate comprehensive pricing summary
            pricing_summary = self._calculate_comprehensive_pricing_summary(
                line_items, 
                project_details.get('delivery_fee', 150.0),
                project_details.get('tax_rate', 0.0825),
                project_details.get('markup_percentage', 0.20)
            )
            bid_package.pricing_summary = pricing_summary
            
            # Step 6: Generate confidence report
            confidence_report = self.generate_bid_confidence_report(comprehensive_analysis)
            bid_package.metadata['confidence_report'] = confidence_report
            
            # Step 7: Convert to dictionary format with source attribution
            result = self._bid_package_to_dict_with_sources(bid_package, comprehensive_analysis)
            
            self.logger.info(f"Comprehensive bid generation completed: {len(line_items)} line items, total: ${pricing_summary.total:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive bid: {e}")
            raise

    def process_official_bid_items(
        self, 
        bid_forms_analysis: ComprehensiveAnalysisResult
    ) -> List[BidLineItem]:
        """
        NEW METHOD: Process official bid line items from bid forms analysis.
        
        Args:
            bid_forms_analysis: Comprehensive analysis results containing bid form data
            
        Returns:
            List of BidLineItem objects with official quantities and descriptions
        """
        official_items = []
        
        try:
            # Extract bid line items from comprehensive analysis
            analyzer_bid_items = bid_forms_analysis.bid_line_items
            
            for analyzer_item in analyzer_bid_items:
                # Match CalTrans item codes to Whitecap products
                product_matches = self._match_caltrans_code_to_products(analyzer_item)
                
                # Apply quantity calculations based on multiple document sources
                calculated_quantity = self._calculate_quantity_from_multiple_sources(
                    analyzer_item, 
                    bid_forms_analysis
                )
                
                # Calculate unit price from product matches
                unit_price = self._calculate_unit_price_from_products(product_matches)
                
                # Determine waste factor based on item type
                waste_factor = self._determine_waste_factor(analyzer_item.description, "bid_form")
                
                # Create official bid line item
                official_item = BidLineItem(
                    item_number=analyzer_item.item_number,
                    description=analyzer_item.description,
                    caltrans_term=analyzer_item.caltrans_code,
                    quantity=calculated_quantity,
                    unit=analyzer_item.unit,
                    unit_price=unit_price,
                    total_price=calculated_quantity * unit_price * (1 + waste_factor),
                    product_matches=product_matches,
                    waste_factor=waste_factor,
                    confidence=analyzer_item.confidence,
                    source_documents=["bid_forms"],
                    cross_references={
                        "official_quantity": analyzer_item.quantity,
                        "official_unit_price": analyzer_item.unit_price,
                        "quantity_variance": abs(calculated_quantity - analyzer_item.quantity) / analyzer_item.quantity if analyzer_item.quantity > 0 else 0
                    }
                )
                
                official_items.append(official_item)
            
            self.logger.info(f"Processed {len(official_items)} official bid items")
            return official_items
            
        except Exception as e:
            self.logger.error(f"Error processing official bid items: {e}")
            return []

    def _generate_line_items_with_context(
        self,
        comprehensive_analysis: ComprehensiveAnalysisResult,
        official_bid_items: List[BidLineItem],
        project_files_dict: Dict[str, str]
    ) -> List[BidLineItem]:
        """
        Generate line items with enhanced document context matching.
        
        Args:
            comprehensive_analysis: Comprehensive analysis results
            official_bid_items: Processed official bid items
            project_files_dict: Dictionary of project files
            
        Returns:
            List of BidLineItem objects with enhanced context
        """
        line_items = []
        
        # Start with official bid items
        line_items.extend(official_bid_items)
        
        # Process additional terms from comprehensive analysis
        for term in comprehensive_analysis.combined_terms:
            # Skip if already covered by official bid items
            if any(item.caltrans_term == term.term for item in line_items):
                continue
            
            # Enhanced product matching with document context
            product_matches = self._enhanced_product_matching_with_context(
                term, 
                comprehensive_analysis, 
                project_files_dict
            )
            
            # Calculate quantity with cross-reference validation
            quantity = self._calculate_quantity_with_validation(
                term, 
                comprehensive_analysis
            )
            
            if quantity <= 0:
                continue
            
            # Calculate unit price
            unit_price = self._calculate_unit_price_from_products(product_matches)
            
            # Determine waste factor
            waste_factor = self._determine_waste_factor(term.term, term.category)
            
            # Create line item with source attribution
            line_item = BidLineItem(
                item_number=f"LI-{len(line_items) + 1:03d}",
                description=f"{term.term.replace('_', ' ').title()} - {term.category}",
                caltrans_term=term.term,
                quantity=quantity,
                unit=self._determine_unit(term.term),
                unit_price=unit_price,
                total_price=quantity * unit_price * (1 + waste_factor),
                product_matches=product_matches,
                waste_factor=waste_factor,
                confidence=term.confidence,
                source_documents=[term.source_document] if hasattr(term, 'source_document') else [],
                cross_references={
                    "found_in_documents": [term.source_document] if hasattr(term, 'source_document') else [],
                    "context": term.context[:200] if term.context else "",
                    "page_number": term.page_number
                }
            )
            
            line_items.append(line_item)
        
        return line_items

    def _enhanced_product_matching_with_context(
        self,
        term: TermMatch,
        comprehensive_analysis: ComprehensiveAnalysisResult,
        project_files_dict: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Enhanced product matching using document context for better accuracy.
        
        Args:
            term: Term match from analysis
            comprehensive_analysis: Comprehensive analysis results
            project_files_dict: Dictionary of project files
            
        Returns:
            List of product matches with enhanced context
        """
        if not self.product_matcher:
            return []
        
        # Get document context for this term
        document_context = self._get_document_context_for_term(term, project_files_dict)
        
        # Build enhanced search terms based on context
        search_terms = self._build_contextual_search_terms(term, document_context)
        
        # Find products with context-aware matching
        products = self.product_matcher.find_products_by_terms(search_terms)
        
        # Apply context-specific confidence adjustments
        for product in products:
            context_confidence = self._calculate_context_confidence(product, document_context)
            product['context_confidence'] = context_confidence
            product['overall_confidence'] = product.get('confidence', 1.0) * context_confidence
        
        # Sort by overall confidence
        products.sort(key=lambda x: x.get('overall_confidence', 0), reverse=True)
        
        return products[:3]  # Return top 3 matches

    def _get_document_context_for_term(
        self, 
        term: TermMatch, 
        project_files_dict: Dict[str, str]
    ) -> Dict[str, Any]:
        """Get document context for a specific term"""
        context = {
            "specifications": {},
            "bid_forms": {},
            "construction_plans": {},
            "supplemental": {}
        }
        
        # Check which documents contain this term
        for doc_type, file_path in project_files_dict.items():
            if doc_type in context:
                # Check if term appears in this document type
                if hasattr(term, 'source_document') and term.source_document == doc_type:
                    context[doc_type] = {
                        "present": True,
                        "confidence": 1.0,
                        "context": term.context if term.context else ""
                    }
                else:
                    context[doc_type] = {
                        "present": False,
                        "confidence": 0.0,
                        "context": ""
                    }
        
        return context

    def _build_contextual_search_terms(
        self, 
        term: TermMatch, 
        document_context: Dict[str, Any]
    ) -> List[str]:
        """Build contextual search terms based on document context"""
        search_terms = [term.term.lower()]
        
        # Add category-specific terms
        if term.category:
            search_terms.append(term.category.lower())
        
        # Add context-specific terms based on document types
        for doc_type, context in document_context.items():
            if context.get("present", False):
                doc_strategy = self.document_context_mapping.get(doc_type, {})
                focus = doc_strategy.get("focus", "")
                if focus:
                    search_terms.append(focus)
        
        # Add base matching strategy terms
        base_strategy = self.matching_strategies.get(term.term.upper(), [])
        search_terms.extend(base_strategy)
        
        return list(set(search_terms))  # Remove duplicates

    def _calculate_context_confidence(
        self, 
        product: Dict[str, Any], 
        document_context: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on document context"""
        confidence = 1.0
        
        # Boost confidence for products that match document focus
        for doc_type, context in document_context.items():
            if context.get("present", False):
                doc_strategy = self.document_context_mapping.get(doc_type, {})
                confidence_boost = doc_strategy.get("confidence_boost", 1.0)
                confidence *= confidence_boost
        
        return min(confidence, 1.5)  # Cap at 1.5x boost

    def _calculate_quantity_with_validation(
        self, 
        term: TermMatch, 
        comprehensive_analysis: ComprehensiveAnalysisResult
    ) -> float:
        """Calculate quantity with cross-reference validation"""
        # Find quantities associated with this term
        associated_quantities = [
            qty for qty in comprehensive_analysis.combined_quantities
            if term.term.lower() in qty.context.lower() or 
               (hasattr(qty, 'source_document') and hasattr(term, 'source_document') and 
                qty.source_document == term.source_document)
        ]
        
        if not associated_quantities:
            return 1.0  # Default quantity
        
        # Calculate weighted average based on source document confidence
        total_weighted_quantity = 0.0
        total_weight = 0.0
        
        for qty in associated_quantities:
            # Weight based on source document type
            weight = self._get_quantity_weight(qty)
            total_weighted_quantity += qty.value * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_weighted_quantity / total_weight
        else:
            return sum(qty.value for qty in associated_quantities) / len(associated_quantities)

    def _get_quantity_weight(self, quantity: ExtractedQuantity) -> float:
        """Get weight for quantity based on source document type"""
        if hasattr(quantity, 'source_document'):
            doc_type = quantity.source_document
            if doc_type == "bid_forms":
                return 1.5  # Highest weight for official bid forms
            elif doc_type == "specifications":
                return 1.2  # High weight for specifications
            elif doc_type == "construction_plans":
                return 1.0  # Standard weight for plans
            elif doc_type == "supplemental":
                return 0.8  # Lower weight for supplemental
        return 1.0  # Default weight

    def _match_caltrans_code_to_products(self, analyzer_item: AnalyzerBidLineItem) -> List[Dict[str, Any]]:
        """Match CalTrans item codes to Whitecap products"""
        if not self.product_matcher:
            return []
        
        # Extract search terms from item description and code
        search_terms = [analyzer_item.caltrans_code.lower()]
        if analyzer_item.description:
            search_terms.extend(analyzer_item.description.lower().split())
        
        # Find products
        products = self.product_matcher.find_products_by_terms(search_terms)
        
        return products[:3]  # Return top 3 matches

    def _calculate_quantity_from_multiple_sources(
        self, 
        analyzer_item: AnalyzerBidLineItem, 
        comprehensive_analysis: ComprehensiveAnalysisResult
    ) -> float:
        """Calculate quantity based on multiple document sources"""
        # Start with official quantity from bid form
        official_quantity = analyzer_item.quantity
        
        # Look for supporting quantities in other documents
        supporting_quantities = []
        for qty in comprehensive_analysis.combined_quantities:
            if (analyzer_item.caltrans_code.lower() in qty.context.lower() or
                analyzer_item.description.lower() in qty.context.lower()):
                supporting_quantities.append(qty)
        
        # If we have supporting quantities, validate against official quantity
        if supporting_quantities:
            avg_supporting = sum(qty.value for qty in supporting_quantities) / len(supporting_quantities)
            
            # If there's significant variance, flag for review
            variance = abs(official_quantity - avg_supporting) / official_quantity if official_quantity > 0 else 0
            if variance > 0.1:  # More than 10% variance
                self.logger.warning(f"Quantity variance detected for {analyzer_item.caltrans_code}: "
                                  f"Official: {official_quantity}, Supporting: {avg_supporting}")
        
        return official_quantity

    def generate_bid_confidence_report(
        self, 
        analysis_results: ComprehensiveAnalysisResult
    ) -> ConfidenceReport:
        """
        NEW METHOD: Generate confidence report for bid generation.
        
        Args:
            analysis_results: Comprehensive analysis results
            
        Returns:
            ConfidenceReport with detailed confidence metrics
        """
        report = ConfidenceReport()
        
        try:
            # Calculate overall confidence
            total_confidence = 0.0
            confidence_count = 0
            
            # Document coverage analysis
            for doc_type, result in analysis_results.individual_results.items():
                coverage = len(result.terminology_found) / max(analysis_results.total_terms, 1)
                report.document_coverage[doc_type] = coverage
                total_confidence += result.confidence_score
                confidence_count += 1
            
            report.overall_confidence = total_confidence / max(confidence_count, 1)
            
            # Quantity confidence analysis
            for qty in analysis_results.combined_quantities:
                if hasattr(qty, 'source_document'):
                    doc_type = qty.source_document
                    if doc_type not in report.quantity_confidence:
                        report.quantity_confidence[doc_type] = []
                    report.quantity_confidence[doc_type].append(qty.value)
            
            # Product match confidence analysis
            for term in analysis_results.combined_terms:
                if hasattr(term, 'source_document'):
                    doc_type = term.source_document
                    if doc_type not in report.product_match_confidence:
                        report.product_match_confidence[doc_type] = []
                    report.product_match_confidence[doc_type].append(term.confidence)
            
            # Cross-reference validation
            if analysis_results.cross_references:
                report.cross_reference_validation = {
                    "term_consistency": analysis_results.cross_references.term_consistency,
                    "quantity_discrepancies": analysis_results.cross_references.quantity_discrepancies,
                    "document_overlap": analysis_results.cross_references.document_overlap
                }
            
            # Identify discrepancies
            for alert in analysis_results.comprehensive_alerts:
                if alert.level.value in ["high", "critical"]:
                    report.discrepancies.append({
                        "level": alert.level.value,
                        "message": alert.message,
                        "details": alert.details
                    })
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(analysis_results, report)
            
            # Identify items requiring manual review
            report.manual_review_items = self._identify_manual_review_items(analysis_results, report)
            
            self.logger.info(f"Confidence report generated: overall confidence {report.overall_confidence:.2f}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating confidence report: {e}")
            return report

    def _generate_recommendations(
        self, 
        analysis_results: ComprehensiveAnalysisResult, 
        report: ConfidenceReport
    ) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Check document coverage
        for doc_type, coverage in report.document_coverage.items():
            if coverage < 0.3:  # Less than 30% coverage
                recommendations.append(f"Consider additional {doc_type} documents for better coverage")
        
        # Check for quantity discrepancies
        if report.cross_reference_validation.get("quantity_discrepancies"):
            recommendations.append("Review quantity discrepancies between documents")
        
        # Check for low confidence items
        low_confidence_terms = [
            term for term in analysis_results.combined_terms 
            if term.confidence < 0.7
        ]
        if low_confidence_terms:
            recommendations.append(f"Review {len(low_confidence_terms)} low-confidence term matches")
        
        # Check for missing critical documents
        if "bid_forms" not in analysis_results.individual_results:
            recommendations.append("Official bid forms recommended for accurate pricing")
        
        if "specifications" not in analysis_results.individual_results:
            recommendations.append("Project specifications recommended for material requirements")
        
        return recommendations

    def _identify_manual_review_items(
        self, 
        analysis_results: ComprehensiveAnalysisResult, 
        report: ConfidenceReport
    ) -> List[str]:
        """Identify items requiring manual review"""
        manual_review_items = []
        
        # Items with high-value quantities
        for qty in analysis_results.combined_quantities:
            if qty.value > 10000:  # High-value items
                manual_review_items.append(f"High-value quantity: {qty.value} {qty.unit} - {qty.context[:50]}")
        
        # Items with low confidence
        for term in analysis_results.combined_terms:
            if term.confidence < 0.6:
                manual_review_items.append(f"Low-confidence term: {term.term} (confidence: {term.confidence:.2f})")
        
        # Items with discrepancies
        for discrepancy in report.discrepancies:
            if discrepancy["level"] in ["high", "critical"]:
                manual_review_items.append(f"Critical discrepancy: {discrepancy['message']}")
        
        return manual_review_items

    def _bid_package_to_dict_with_sources(
        self, 
        bid_package: BidPackage, 
        comprehensive_analysis: ComprehensiveAnalysisResult
    ) -> Dict[str, Any]:
        """Convert bid package to dictionary with source attribution"""
        result = self._bid_package_to_dict(bid_package)
        
        # Add comprehensive analysis metadata
        result['comprehensive_analysis'] = {
            'total_documents': comprehensive_analysis.total_documents,
            'total_terms': comprehensive_analysis.total_terms,
            'total_quantities': comprehensive_analysis.total_quantities,
            'total_alerts': comprehensive_analysis.total_alerts,
            'overall_confidence': comprehensive_analysis.overall_confidence,
            'processing_time': comprehensive_analysis.processing_time,
            'document_results': {
                doc_type: {
                    'terms_found': len(result.terminology_found),
                    'quantities_found': len(result.quantities),
                    'confidence_score': result.confidence_score,
                    'processing_time': result.processing_time
                }
                for doc_type, result in comprehensive_analysis.individual_results.items()
            }
        }
        
        # Add source attribution to line items
        for line_item in result['line_items']:
            line_item['source_attribution'] = {
                'source_documents': line_item.get('source_documents', []),
                'cross_references': line_item.get('cross_references', {}),
                'confidence': line_item.get('confidence', 1.0)
            }
        
        return result

    def _bid_package_to_dict(self, bid_package: BidPackage) -> Dict[str, Any]:
        """Convert bid package to dictionary format"""
        return {
            "project_name": bid_package.project_name,
            "project_number": bid_package.project_number,
            "bid_date": bid_package.bid_date.isoformat(),
            "markup_percentage": bid_package.markup_percentage,
            "delivery_fee": bid_package.delivery_fee,
            "notes": bid_package.notes,
            "line_items": [
                {
                    "item_number": item.item_number,
                    "description": item.description,
                    "caltrans_term": item.caltrans_term,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "waste_factor": item.waste_factor,
                    "markup_percentage": item.markup_percentage,
                    "delivery_fee": item.delivery_fee,
                    "notes": item.notes,
                    "confidence": item.confidence,
                    "product_matches": item.product_matches,
                    "source_documents": item.source_documents,
                    "cross_references": item.cross_references
                }
                for item in bid_package.line_items
            ],
            "pricing_summary": {
                "subtotal": bid_package.pricing_summary.subtotal,
                "markup_amount": bid_package.pricing_summary.markup_amount,
                "delivery_fee": bid_package.pricing_summary.delivery_fee,
                "waste_adjustments": bid_package.pricing_summary.waste_adjustments,
                "total": bid_package.pricing_summary.total,
                "line_item_count": bid_package.pricing_summary.line_item_count,
                "high_priority_items": bid_package.pricing_summary.high_priority_items,
                "estimated_materials_cost": bid_package.pricing_summary.estimated_materials_cost,
                "estimated_labor_cost": bid_package.pricing_summary.estimated_labor_cost
            },
            "analysis_metadata": {
                "total_terms_found": len(bid_package.analysis_results.terminology_found) if bid_package.analysis_results else 0,
                "total_quantities": len(bid_package.analysis_results.quantities) if bid_package.analysis_results else 0,
                "high_priority_terms": bid_package.analysis_results.high_priority_terms if bid_package.analysis_results else 0,
                "critical_alerts": bid_package.analysis_results.critical_alerts if bid_package.analysis_results else 0
            } if bid_package.analysis_results else {},
            "metadata": bid_package.metadata
        }

    def _calculate_comprehensive_pricing_summary(
        self,
        line_items: List[BidLineItem],
        delivery_fee: float,
        tax_rate: float,
        markup_percentage: float
    ) -> PricingSummary:
        """Calculate comprehensive pricing summary with tax and delivery"""
        
        # Calculate subtotal
        subtotal = sum(item.total_price for item in line_items)
        
        # Calculate markup
        markup_amount = subtotal * markup_percentage
        
        # Calculate waste adjustments
        waste_adjustments = sum(
            item.total_price * item.waste_factor for item in line_items
        )
        
        # Calculate delivery fee (use provided amount or calculate based on subtotal)
        if delivery_fee <= 0:
            delivery_fee = max(
                PricingConfig.DELIVERY_MINIMUM,
                subtotal * PricingConfig.DELIVERY_PERCENTAGE
            )
        
        # Calculate tax
        taxable_amount = subtotal + markup_amount + waste_adjustments
        tax_amount = taxable_amount * tax_rate
        
        # Calculate total
        total = subtotal + markup_amount + waste_adjustments + delivery_fee + tax_amount
        
        return PricingSummary(
            subtotal=subtotal,
            markup_amount=markup_amount,
            delivery_fee=delivery_fee,
            waste_adjustments=waste_adjustments,
            total=total,
            line_item_count=len(line_items),
            high_priority_items=len([item for item in line_items if item.confidence > 0.8]),
            estimated_materials_cost=subtotal,
            estimated_labor_cost=markup_amount
        )

    def find_products_for_term(self, term_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find matching products for a CalTrans term.
        
        Args:
            term_data: Dictionary containing term information
            
        Returns:
            List of matching products with scores and pricing
        """
        if not self.product_matcher:
            return []
        
        term = term_data.get("term", "")
        category = term_data.get("category", "")
        
        # Get matching strategy for this term
        search_terms = self.matching_strategies.get(term.upper(), [term.lower()])
        
        # Add category-specific terms
        if category:
            search_terms.extend([category.lower()])
        
        # Find products
        products = self.product_matcher.find_products_by_terms(search_terms)
        
        # Limit to top 3 matches
        return products[:3]

    def calculate_quantity_needed(self, term_data: Dict[str, Any], all_quantities: List[ExtractedQuantity]) -> float:
        """
        Calculate the quantity needed for a specific term.
        
        Args:
            term_data: Dictionary containing term information
            all_quantities: List of all extracted quantities
            
        Returns:
            Calculated quantity needed
        """
        term = term_data.get("term", "")
        context = term_data.get("context", "")
        
        # Find associated quantities
        associated_quantities = []
        for quantity in all_quantities:
            # Check if quantity is associated with this term
            if (term.lower() in quantity.context.lower() or 
                quantity.context.lower() in context.lower()):
                associated_quantities.append(quantity)
        
        if not associated_quantities:
            # If no direct association, use the first quantity with matching unit
            term_factors = self.quantity_factors.get(term.upper(), {})
            target_unit = term_factors.get("unit", "EA")
            
            for quantity in all_quantities:
                if quantity.unit == target_unit:
                    associated_quantities.append(quantity)
                    break
        
        # Calculate total quantity
        total_quantity = sum(q.value for q in associated_quantities)
        
        # Apply base factor if available
        term_factors = self.quantity_factors.get(term.upper(), {})
        base_factor = term_factors.get("base_factor", 1.0)
        
        return total_quantity * base_factor

    def calculate_pricing_summary(self, bid_line_items: List[BidLineItem]) -> Dict[str, Any]:
        """
        Calculate pricing summary for bid line items.
        
        Args:
            bid_line_items: List of bid line items
            
        Returns:
            Dictionary containing pricing summary
        """
        subtotal = sum(item.total_price for item in bid_line_items)
        
        # Calculate markup (using average markup from line items)
        if bid_line_items:
            avg_markup = sum(item.markup_percentage for item in bid_line_items) / len(bid_line_items)
            markup_amount = subtotal * avg_markup
        else:
            markup_amount = 0.0
        
        # Calculate waste adjustments
        waste_adjustments = sum(
            item.total_price * item.waste_factor for item in bid_line_items
        )
        
        # Calculate delivery fee
        delivery_fee = self._calculate_delivery_fee(subtotal)
        
        # Calculate total
        total = subtotal + markup_amount + waste_adjustments + delivery_fee
        
        # Count high priority items
        high_priority_items = len([
            item for item in bid_line_items 
            if any("high" in match.get("quality", "").lower() 
                   for match in item.product_matches)
        ])
        
        # Estimate materials and labor costs
        estimated_materials_cost = subtotal * 0.7  # 70% materials
        estimated_labor_cost = subtotal * 0.3      # 30% labor
        
        summary = PricingSummary(
            subtotal=subtotal,
            markup_amount=markup_amount,
            delivery_fee=delivery_fee,
            waste_adjustments=waste_adjustments,
            total=total,
            line_item_count=len(bid_line_items),
            high_priority_items=high_priority_items,
            estimated_materials_cost=estimated_materials_cost,
            estimated_labor_cost=estimated_labor_cost
        )
        
        return {
            "subtotal": summary.subtotal,
            "markup_amount": summary.markup_amount,
            "delivery_fee": summary.delivery_fee,
            "waste_adjustments": summary.waste_adjustments,
            "total": summary.total,
            "line_item_count": summary.line_item_count,
            "high_priority_items": summary.high_priority_items,
            "estimated_materials_cost": summary.estimated_materials_cost,
            "estimated_labor_cost": summary.estimated_labor_cost
        }

    def _generate_line_items_from_analysis(self, analysis_result: CalTransAnalysisResult) -> List[BidLineItem]:
        """Generate line items from CalTrans analysis results"""
        line_items = []
        item_number = 1
        
        # Group terms by category for better organization
        terms_by_category = {}
        for term in analysis_result.terminology_found:
            category = term.category
            if category not in terms_by_category:
                terms_by_category[category] = []
            terms_by_category[category].append(term)
        
        # Generate line items for each category
        for category, terms in terms_by_category.items():
            for term in terms:
                try:
                    # Calculate quantity needed
                    quantity = self.calculate_quantity_needed(
                        {"term": term.term, "context": term.context},
                        analysis_result.quantities
                    )
                    
                    if quantity <= 0:
                        continue
                    
                    # Find matching products
                    products = self.find_products_for_term({
                        "term": term.term,
                        "category": term.category
                    })
                    
                    # Calculate unit price from best product match
                    unit_price = self._calculate_unit_price_from_products(products)
                    
                    # Determine waste factor
                    waste_factor = self._determine_waste_factor(term.term, term.category)
                    
                    # Calculate total price
                    total_price = quantity * unit_price * (1 + waste_factor)
                    
                    # Create line item
                    line_item = BidLineItem(
                        item_number=f"{item_number:03d}",
                        description=f"{term.term} - {term.category}",
                        caltrans_term=term.term,
                        quantity=quantity,
                        unit=self._determine_unit(term.term),
                        unit_price=unit_price,
                        total_price=total_price,
                        product_matches=products,
                        waste_factor=waste_factor,
                        notes=f"Page {term.page_number}: {term.context[:100]}..."
                    )
                    
                    line_items.append(line_item)
                    item_number += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error generating line item for term {term.term}: {e}")
                    continue
        
        return line_items

    def _calculate_unit_price_from_products(self, products: List[Dict[str, Any]]) -> float:
        """Calculate unit price from product matches"""
        if not products:
            return 0.0
        
        # Use the best match (first product)
        best_product = products[0]
        
        # Use actual price if available, otherwise estimated price
        price = best_product.get("price") or best_product.get("estimated_price", 0.0)
        
        return price

    def _determine_waste_factor(self, term: str, category: str) -> float:
        """Determine waste factor for a term/category"""
        term_upper = term.upper()
        
        # Check for specific term-based waste factors
        if "FORM" in term_upper or "PLYWOOD" in term_upper:
            return PricingConfig.WASTE_FACTORS["formwork"]
        elif "LUMBER" in term_upper or "2X" in term_upper or "4X" in term_upper:
            return PricingConfig.WASTE_FACTORS["lumber"]
        elif "BOLT" in term_upper or "SCREW" in term_upper or "NAIL" in term_upper:
            return PricingConfig.WASTE_FACTORS["hardware"]
        elif "SPECIAL" in term_upper or "CUSTOM" in term_upper:
            return PricingConfig.WASTE_FACTORS["specialty"]
        
        # Check category-based waste factors
        category_lower = category.lower()
        if "formwork" in category_lower:
            return PricingConfig.WASTE_FACTORS["formwork"]
        elif "lumber" in category_lower:
            return PricingConfig.WASTE_FACTORS["lumber"]
        elif "hardware" in category_lower:
            return PricingConfig.WASTE_FACTORS["hardware"]
        
        return PricingConfig.WASTE_FACTORS["default"]

    def _determine_unit(self, term: str) -> str:
        """Determine the appropriate unit for a term"""
        term_upper = term.upper()
        
        # Check quantity factors for specific terms
        if term_upper in self.quantity_factors:
            return self.quantity_factors[term_upper]["unit"]
        
        # Default unit determination based on term content
        if any(word in term_upper for word in ["BALUSTER", "BLOCKOUT", "POST", "PIECE"]):
            return "EA"
        elif any(word in term_upper for word in ["WALL", "FORM", "FINISH", "TEXTURE"]):
            return "SQFT"
        elif any(word in term_upper for word in ["RAIL", "FENCE", "CONTROL"]):
            return "LF"
        elif any(word in term_upper for word in ["CONCRETE", "MATERIAL"]):
            return "CY"
        
        return "EA"  # Default to each

    def _calculate_delivery_fee(self, subtotal: float) -> float:
        """Calculate delivery fee based on subtotal"""
        delivery_fee = subtotal * PricingConfig.DELIVERY_PERCENTAGE
        return max(delivery_fee, PricingConfig.DELIVERY_MINIMUM)

    def save_bid_to_file(self, bid_data: Dict[str, Any], output_path: str) -> None:
        """Save bid data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(bid_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Bid saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving bid to file: {e}")
            raise

    def load_bid_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load bid data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bid_data = json.load(f)
            self.logger.info(f"Bid loaded from: {file_path}")
            return bid_data
        except Exception as e:
            self.logger.error(f"Error loading bid from file: {e}")
            raise


def create_bidding_engine() -> CalTransBiddingEngine:
    """Factory function to create a CalTransBiddingEngine instance"""
    return CalTransBiddingEngine()


# Example usage and testing functions
def test_bidding_engine():
    """Test the CalTransBiddingEngine functionality"""
    engine = CalTransBiddingEngine()
    
    # Test product matching
    term_data = {"term": "BALUSTER", "category": "bridge_barrier"}
    products = engine.find_products_for_term(term_data)
    print(f"Found {len(products)} products for BALUSTER")
    
    # Test quantity calculation
    quantities = [
        ExtractedQuantity(value=100.0, unit="EA", context="baluster installation", page_number=1),
        ExtractedQuantity(value=50.0, unit="LF", context="railing length", page_number=1)
    ]
    quantity_needed = engine.calculate_quantity_needed(term_data, quantities)
    print(f"Quantity needed for BALUSTER: {quantity_needed}")
    
    # Test pricing summary
    line_items = [
        BidLineItem(
            item_number="001",
            description="Test Item",
            caltrans_term="BALUSTER",
            quantity=100.0,
            unit="EA",
            unit_price=25.0,
            total_price=2500.0
        )
    ]
    pricing = engine.calculate_pricing_summary(line_items)
    print(f"Pricing summary: {pricing}")
    
    return engine


if __name__ == "__main__":
    test_bidding_engine() 