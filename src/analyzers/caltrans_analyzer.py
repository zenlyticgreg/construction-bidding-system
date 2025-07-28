"""
CalTrans PDF Analyzer for Bidding System

This module provides comprehensive analysis of CalTrans project PDFs including:
- Terminology detection and cross-referencing
- Quantity extraction using regex patterns
- High-priority construction term identification
- Lumber requirement calculations
- Alert generation for critical items
- Structured analysis results
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback

# Third-party imports
import pdfplumber
import pandas as pd
from fuzzywuzzy import fuzz

# Local imports
try:
    from config.settings import get_setting
    from utils.data_validator import ValidationResult, ValidationLevel
except ImportError:
    # Fallback for testing without full project structure
    def get_setting(key: str, default: Any = None) -> Any:
        """Fallback settings function for testing"""
        return default
    
    class ValidationResult:
        """Fallback validation result for testing"""
        def __init__(self, is_valid: bool, level: str, message: str):
            self.is_valid = is_valid
            self.level = level
            self.message = message
    
    class ValidationLevel:
        """Fallback validation level for testing"""
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class QuantityUnit(Enum):
    """Supported quantity units"""
    SQFT = "SQFT"
    LF = "LF"
    CY = "CY"
    EA = "EA"
    TON = "TON"
    GAL = "GAL"
    LB = "LB"


@dataclass
class ExtractedQuantity:
    """Represents an extracted quantity with context"""
    value: float
    unit: str
    context: str
    page_number: int
    item: str = "Construction Item"
    confidence: float = 1.0
    line_number: Optional[int] = None
    term_associated: Optional[str] = None
    source_document: str = "unknown"


@dataclass
class TermMatch:
    """Represents a found CalTrans term with context"""
    term: str
    category: str
    priority: str
    context: str
    page_number: int
    confidence: float = 1.0
    line_number: Optional[int] = None
    quantities: List[ExtractedQuantity] = field(default_factory=list)
    source_document: str = "unknown"


@dataclass
class Alert:
    """Represents an analysis alert"""
    level: AlertLevel
    message: str
    term: Optional[str] = None
    quantity: Optional[ExtractedQuantity] = None
    page_number: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SheetAnalysis:
    """Analysis results for a single PDF page/sheet"""
    page_number: int
    text_content: str
    terms_found: List[TermMatch] = field(default_factory=list)
    quantities_found: List[ExtractedQuantity] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)
    processing_time: float = 0.0
    text_extraction_quality: float = 1.0


@dataclass
class LumberRequirements:
    """Calculated lumber requirements"""
    total_board_feet: float = 0.0
    plywood_sheets: float = 0.0
    dimensional_lumber: Dict[str, float] = field(default_factory=dict)
    formwork_area: float = 0.0
    waste_factor: float = 0.15
    reuse_factor: float = 3.0
    estimated_cost: float = 0.0


@dataclass
class BidLineItem:
    """Represents a bid line item extracted from bid forms"""
    item_number: str
    description: str
    caltrans_code: str
    quantity: float
    unit: str
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    source_document: str = "bid_forms"
    confidence: float = 1.0
    notes: str = ""
    term_matches: List[str] = field(default_factory=list)


@dataclass
class CrossReferenceResult:
    """Results of cross-referencing findings across documents"""
    term_consistency: Dict[str, List[str]] = field(default_factory=dict)  # term -> list of documents
    quantity_discrepancies: List[Dict[str, Any]] = field(default_factory=list)
    missing_requirements: List[Dict[str, Any]] = field(default_factory=list)
    document_coverage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class CalTransAnalysisResult:
    """Complete analysis result for a CalTrans PDF"""
    pdf_path: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    total_pages: int = 0
    processing_time: float = 0.0
    document_type: str = "general"  # Added document type
    
    # Analysis results
    terminology_found: List[TermMatch] = field(default_factory=list)
    quantities: List[ExtractedQuantity] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)
    sheet_analyses: List[SheetAnalysis] = field(default_factory=list)
    
    # Calculated requirements
    total_lumber_requirements: LumberRequirements = field(default_factory=LumberRequirements)
    
    # Summary statistics
    high_priority_terms: int = 0
    total_quantities: int = 0
    critical_alerts: int = 0
    
    # Quality metrics
    text_extraction_quality: float = 1.0
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "pdf_path": self.pdf_path,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "total_pages": self.total_pages,
            "processing_time": self.processing_time,
            "terminology_found": [
                {
                    "term": t.term,
                    "category": t.category,
                    "priority": t.priority,
                    "context": t.context,
                    "page_number": t.page_number,
                    "confidence": t.confidence
                } for t in self.terminology_found
            ],
            "quantities": [
                {
                    "value": q.value,
                    "unit": q.unit,
                    "context": q.context,
                    "page_number": q.page_number,
                    "confidence": q.confidence
                } for q in self.quantities
            ],
            "alerts": [
                {
                    "level": a.level.value,
                    "message": a.message,
                    "term": a.term,
                    "page_number": a.page_number
                } for a in self.alerts
            ],
            "lumber_requirements": {
                "total_board_feet": self.total_lumber_requirements.total_board_feet,
                "plywood_sheets": self.total_lumber_requirements.plywood_sheets,
                "dimensional_lumber": self.total_lumber_requirements.dimensional_lumber,
                "formwork_area": self.total_lumber_requirements.formwork_area,
                "estimated_cost": self.total_lumber_requirements.estimated_cost
            },
            "summary": {
                "high_priority_terms": self.high_priority_terms,
                "total_quantities": self.total_quantities,
                "critical_alerts": self.critical_alerts,
                "text_extraction_quality": self.text_extraction_quality,
                "confidence_score": self.confidence_score
            }
        }


@dataclass
class ComprehensiveAnalysisResult:
    """Complete analysis result for multiple project documents"""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    total_documents: int = 0
    processing_time: float = 0.0
    
    # Individual document results
    individual_results: Dict[str, CalTransAnalysisResult] = field(default_factory=dict)
    
    # Cross-reference analysis
    cross_references: CrossReferenceResult = field(default_factory=CrossReferenceResult)
    
    # Combined results
    combined_terms: List[TermMatch] = field(default_factory=list)
    combined_quantities: List[ExtractedQuantity] = field(default_factory=list)
    bid_line_items: List[BidLineItem] = field(default_factory=list)
    
    # Comprehensive alerts
    comprehensive_alerts: List[Alert] = field(default_factory=list)
    
    # Summary statistics
    total_terms: int = 0
    total_quantities: int = 0
    total_alerts: int = 0
    overall_confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "total_documents": self.total_documents,
            "processing_time": self.processing_time,
            "individual_results": {
                doc_type: result.to_dict() 
                for doc_type, result in self.individual_results.items()
            },
            "cross_references": {
                "term_consistency": self.cross_references.term_consistency,
                "quantity_discrepancies": self.cross_references.quantity_discrepancies,
                "missing_requirements": self.cross_references.missing_requirements,
                "document_coverage": self.cross_references.document_coverage,
                "confidence_scores": self.cross_references.confidence_scores
            },
            "combined_terms": [
                {
                    "term": t.term,
                    "category": t.category,
                    "priority": t.priority,
                    "context": t.context,
                    "page_number": t.page_number,
                    "confidence": t.confidence,
                    "source_document": getattr(t, 'source_document', 'unknown')
                } for t in self.combined_terms
            ],
            "combined_quantities": [
                {
                    "value": q.value,
                    "unit": q.unit,
                    "context": q.context,
                    "page_number": q.page_number,
                    "confidence": q.confidence,
                    "source_document": getattr(q, 'source_document', 'unknown')
                } for q in self.combined_quantities
            ],
            "bid_line_items": [
                {
                    "item_number": item.item_number,
                    "description": item.description,
                    "caltrans_code": item.caltrans_code,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "source_document": item.source_document,
                    "confidence": item.confidence,
                    "notes": item.notes,
                    "term_matches": item.term_matches
                } for item in self.bid_line_items
            ],
            "comprehensive_alerts": [
                {
                    "level": a.level.value,
                    "message": a.message,
                    "term": a.term,
                    "page_number": a.page_number,
                    "details": a.details
                } for a in self.comprehensive_alerts
            ],
            "summary": {
                "total_terms": self.total_terms,
                "total_quantities": self.total_quantities,
                "total_alerts": self.total_alerts,
                "overall_confidence": self.overall_confidence
            }
        }


class CalTransPDFAnalyzer:
    """Main analyzer class for CalTrans PDFs"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the analyzer"""
        self.logger = logger or self._setup_logger()
        self.settings = get_setting('FILE_UPLOAD_CONFIG', {})
        
        # Load CalTrans reference data
        self.caltrans_reference = self._load_caltrans_reference()
        
        # Compile regex patterns for quantity extraction
        self.quantity_patterns = self._compile_quantity_patterns()
        
        # Document-specific patterns and strategies
        self.document_strategies = self._setup_document_strategies()
        
        # High-priority terms to detect
        self.high_priority_terms = {
            "BALUSTER", "BLOCKOUT", "STAMPED_CONCRETE", "FRACTURED_RIB_TEXTURE",
            "RETAINING_WALL", "EROSION_CONTROL", "FALSEWORK", "FORM_FACING",
            "TYPE_86H_RAIL", "ARCHITECTURAL_TREATMENT"
        }
        
        # Bid form patterns for line item extraction
        self.bid_form_patterns = self._compile_bid_form_patterns()
        
        # Lumber calculation constants
        self.lumber_constants = {
            "board_feet_per_sqft_formwork": 0.5,
            "plywood_sheets_per_sqft": 0.032,  # 4x8 sheet = 32 sqft
            "dimensional_lumber_rates": {
                "2x4": 0.5,  # board feet per linear foot
                "2x6": 0.75,
                "2x8": 1.0,
                "2x10": 1.25,
                "2x12": 1.5,
                "4x4": 1.33,
                "6x6": 3.0
            },
            "material_costs": {
                "plywood_per_sheet": 45.0,
                "dimensional_lumber_per_bf": 2.5,
                "formwork_labor_per_sqft": 8.0
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for analysis operations"""
        logger = logging.getLogger("caltrans_analyzer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_caltrans_reference(self) -> Dict[str, Any]:
        """Load CalTrans reference data"""
        try:
            # Try multiple possible paths
            possible_paths = [
                Path("data/caltrans_reference.json"),
                Path(__file__).parent.parent.parent / "data" / "caltrans_reference.json",
                Path.cwd() / "data" / "caltrans_reference.json"
            ]
            
            for reference_path in possible_paths:
                if reference_path.exists():
                    with open(reference_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            self.logger.warning("CalTrans reference file not found in any expected location")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading CalTrans reference: {e}")
            return {}
    
    def _compile_quantity_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for quantity extraction"""
        patterns = {}
        
        # Try to load patterns from reference data first
        if self.caltrans_reference and "quantity_patterns" in self.caltrans_reference:
            ref_patterns = self.caltrans_reference["quantity_patterns"]["measurement_units"]
            for unit, unit_data in ref_patterns.items():
                patterns[unit] = []
                for pattern_str in unit_data["regex_patterns"]:
                    patterns[unit].append(re.compile(pattern_str, re.IGNORECASE))
        
        # Fallback to hardcoded patterns if reference data is not available
        if not patterns:
            # Square feet patterns
            patterns["SQFT"] = [
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:SQ\s*FT|SQFT|SF|SQUARE\s*FEET?)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:SQ\s*YARDS?|SQYD|SY)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:SQ\s*METERS?|SQM)", re.IGNORECASE)
            ]
            
            # Linear feet patterns
            patterns["LF"] = [
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:LF|LINEAR\s*FEET?|LINEAR\s*FT)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:LY|LINEAR\s*YARDS?)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:LM|LINEAR\s*METERS?)", re.IGNORECASE)
            ]
            
            # Cubic yards patterns
            patterns["CY"] = [
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:CY|CUBIC\s*YARDS?|CU\s*YD)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:CF|CUBIC\s*FEET?|CU\s*FT)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:CM|CUBIC\s*METERS?|CU\s*M)", re.IGNORECASE)
            ]
            
            # Each patterns
            patterns["EA"] = [
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:EA|EACH|EACHES?)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:PCS?|PIECES?)", re.IGNORECASE),
                re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:UNITS?|UN)", re.IGNORECASE)
            ]
        
        return patterns
    
    def analyze_pdf_with_progress(self, pdf_content: bytes, progress_callback=None) -> CalTransAnalysisResult:
        """
        Analyze a CalTrans PDF with progress tracking
        
        Args:
            pdf_content: PDF content as bytes
            progress_callback: Callback function for progress updates
                Signature: callback(current_page, total_pages, terms_count, quantities_count, elapsed_time)
            
        Returns:
            CalTransAnalysisResult with complete analysis
        """
        start_time = datetime.now()
        
        self.logger.info("Starting analysis of PDF with progress tracking")
        
        # Initialize result
        result = CalTransAnalysisResult(pdf_path="uploaded_pdf")
        
        try:
            import io
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                result.total_pages = len(pdf.pages)
                self.logger.info(f"PDF has {result.total_pages} pages")
                
                total_terms = 0
                total_quantities = 0
                
                # Analyze each page
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.info(f"Analyzing page {page_num}/{result.total_pages}")
                    
                    # Extract text from page
                    text = page.extract_text() or ""
                    
                    # Analyze the page
                    sheet_analysis = self.analyze_page(text, page_num)
                    result.sheet_analyses.append(sheet_analysis)
                    
                    # Aggregate results
                    result.terminology_found.extend(sheet_analysis.terms_found)
                    result.quantities.extend(sheet_analysis.quantities_found)
                    result.alerts.extend(sheet_analysis.alerts)
                    
                    # Update counters
                    total_terms = len(result.terminology_found)
                    total_quantities = len(result.quantities)
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    
                    # Call progress callback if provided
                    if progress_callback:
                        try:
                            progress_callback(page_num, result.total_pages, total_terms, total_quantities, elapsed_time)
                        except Exception as e:
                            self.logger.warning(f"Progress callback failed: {e}")
                
                # Calculate lumber requirements
                result.total_lumber_requirements = self.calculate_lumber_requirements(
                    result.terminology_found, result.quantities
                )
                
                # Generate summary statistics
                result.high_priority_terms = len([
                    t for t in result.terminology_found 
                    if t.priority in ["high", "critical"]
                ])
                result.total_quantities = len(result.quantities)
                result.critical_alerts = len([
                    a for a in result.alerts 
                    if a.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]
                ])
                
                # Calculate quality metrics
                if result.sheet_analyses:
                    result.text_extraction_quality = sum(
                        sa.text_extraction_quality for sa in result.sheet_analyses
                    ) / len(result.sheet_analyses)
                
                result.processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"Analysis completed in {result.processing_time:.2f} seconds")
                self.logger.info(f"Found {len(result.terminology_found)} terms, {len(result.quantities)} quantities")
                
        except Exception as e:
            self.logger.error(f"Error analyzing PDF: {e}")
            self.logger.error(traceback.format_exc())
            raise
        
        return result

    def analyze_pdf(self, pdf_path: str, document_type: str = "general") -> CalTransAnalysisResult:
        """
        Analyze a CalTrans PDF file with document-specific strategies.
        
        Args:
            pdf_path: Path to the PDF file to analyze
            document_type: Type of document ("specifications", "bid_forms", "construction_plans", "supplemental", "general")
            
        Returns:
            CalTransAnalysisResult with complete analysis
        """
        start_time = datetime.now()
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Starting analysis of {document_type} PDF: {pdf_path}")
        
        # Initialize result with document type
        result = CalTransAnalysisResult(pdf_path=str(pdf_path), document_type=document_type)
        
        # Get document-specific strategy
        strategy = self.document_strategies.get(document_type, self.document_strategies["general"])
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result.total_pages = len(pdf.pages)
                self.logger.info(f"PDF has {result.total_pages} pages")
                
                # Analyze each page
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.info(f"Analyzing page {page_num}/{result.total_pages}")
                    
                    # Extract text from page
                    text = page.extract_text() or ""
                    
                    # Analyze the page with document-specific strategy
                    sheet_analysis = self.analyze_page(text, page_num, document_type, strategy)
                    result.sheet_analyses.append(sheet_analysis)
                    
                    # Aggregate results
                    result.terminology_found.extend(sheet_analysis.terms_found)
                    result.quantities.extend(sheet_analysis.quantities_found)
                    result.alerts.extend(sheet_analysis.alerts)
                
                # Calculate lumber requirements
                result.total_lumber_requirements = self.calculate_lumber_requirements(
                    result.terminology_found, result.quantities
                )
                
                # Generate summary statistics
                result.high_priority_terms = len([
                    t for t in result.terminology_found 
                    if t.priority in ["high", "critical"]
                ])
                result.total_quantities = len(result.quantities)
                result.critical_alerts = len([
                    a for a in result.alerts 
                    if a.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]
                ])
                
                # Calculate quality metrics
                if result.sheet_analyses:
                    result.text_extraction_quality = sum(
                        sa.text_extraction_quality for sa in result.sheet_analyses
                    ) / len(result.sheet_analyses)
                
                # Apply document-specific confidence boost
                confidence_boost = strategy.get("confidence_boost", 1.0)
                base_confidence = self._calculate_confidence_score(result)
                result.confidence_score = min(1.0, base_confidence * confidence_boost)
                
                result.processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"{document_type} analysis completed in {result.processing_time:.2f} seconds")
                self.logger.info(f"Found {len(result.terminology_found)} terms, {len(result.quantities)} quantities, "
                               f"confidence: {result.confidence_score:.2f}")
                
        except Exception as e:
            self.logger.error(f"Error analyzing {document_type} PDF: {e}")
            self.logger.error(traceback.format_exc())
            raise
        
        return result
    
    def analyze_page(self, text: str, page_num: int, document_type: str = "general", strategy: Dict[str, Any] = None) -> SheetAnalysis:
        """
        Analyze a single page of text with document-specific strategies
        
        Args:
            text: Text content from the page
            page_num: Page number
            document_type: Type of document for specialized analysis
            strategy: Document-specific analysis strategy
            
        Returns:
            SheetAnalysis with page-specific results
        """
        start_time = datetime.now()
        
        # Initialize sheet analysis
        sheet_analysis = SheetAnalysis(
            page_number=page_num,
            text_content=text
        )
        
        # Use document-specific strategy if provided
        if strategy is None:
            strategy = self.document_strategies.get(document_type, self.document_strategies["general"])
        
        # Extract quantities with document-specific patterns
        quantities = self._extract_quantities(text, page_num, document_type, strategy)
        sheet_analysis.quantities_found = quantities
        
        # Find CalTrans terms with document-specific focus
        terms = self._find_caltrans_terms(text, page_num, quantities, document_type, strategy)
        sheet_analysis.terms_found = terms
        
        # Generate alerts
        alerts = self._generate_alerts(terms, quantities, page_num)
        sheet_analysis.alerts = alerts
        
        # Calculate text extraction quality
        sheet_analysis.text_extraction_quality = self._calculate_text_quality(text)
        
        sheet_analysis.processing_time = (datetime.now() - start_time).total_seconds()
        
        return sheet_analysis
    
    def _extract_quantities(self, text: str, page_num: int, document_type: str = "general", strategy: Dict[str, Any] = None) -> List[ExtractedQuantity]:
        """Extract quantities from text using document-specific patterns"""
        quantities = []
        
        # Use document-specific strategy if provided
        if strategy is None:
            strategy = self.document_strategies.get(document_type, self.document_strategies["general"])
        
        # Split text into lines for better context
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for unit, patterns in self.quantity_patterns.items():
                for pattern in patterns:
                    matches = pattern.finditer(line)
                    for match in matches:
                        try:
                            value_str = match.group(1).replace(',', '')
                            value = float(value_str)
                            
                            # Extract context around the match
                            context = self.extract_context(line, match.group(0), 50)
                            
                            # Apply document-specific confidence adjustments
                            base_confidence = 1.0
                            if document_type == "bid_forms":
                                # Higher confidence for quantities in bid forms
                                base_confidence = 1.2
                            elif document_type == "specifications":
                                # High confidence for specifications
                                base_confidence = 1.1
                            elif document_type == "construction_plans":
                                # Medium confidence for plans
                                base_confidence = 0.9
                            elif document_type == "supplemental":
                                # Lower confidence for supplemental documents
                                base_confidence = 0.8
                            
                            quantity = ExtractedQuantity(
                                value=value,
                                unit=unit,
                                context=context,
                                page_number=page_num,
                                line_number=line_num,
                                confidence=min(1.0, base_confidence)
                            )
                            quantities.append(quantity)
                            
                        except (ValueError, AttributeError) as e:
                            self.logger.warning(f"Error parsing quantity: {e}")
        
        return quantities
    
    def _find_caltrans_terms(self, text: str, page_num: int, quantities: List[ExtractedQuantity], document_type: str = "general", strategy: Dict[str, Any] = None) -> List[TermMatch]:
        """Find CalTrans terms in text with document-specific focus"""
        terms = []
        
        # Use document-specific strategy if provided
        if strategy is None:
            strategy = self.document_strategies.get(document_type, self.document_strategies["general"])
        
        # Get focus terms for this document type
        focus_terms = strategy.get("focus_terms", [])
        
        # Check all term categories
        term_categories = [
            ("bridge_barrier_terms", "bridge_barrier"),
            ("formwork_terms", "formwork"),
            ("concrete_terms", "concrete"),
            ("temporary_structures", "temporary_structures")
        ]
        
        for category_key, category_name in term_categories:
            category_terms = self.caltrans_reference.get(category_key, {})
            
            for term, term_data in category_terms.items():
                if self._term_in_text(term, text):
                    # Extract context
                    context = self.extract_context(text, term, 100)
                    
                    # Find associated quantities
                    associated_quantities = self._find_associated_quantities(
                        term, quantities, context
                    )
                    
                    # Apply document-specific confidence adjustments
                    base_confidence = 1.0
                    if document_type == "specifications":
                        # Higher confidence for specifications
                        base_confidence = 1.2
                    elif document_type == "bid_forms":
                        # High confidence for bid forms
                        base_confidence = 1.1
                    elif document_type == "construction_plans":
                        # Medium confidence for plans
                        base_confidence = 0.9
                    elif document_type == "supplemental":
                        # Lower confidence for supplemental documents
                        base_confidence = 0.8
                    
                    # Boost confidence for focus terms
                    if any(focus_term in term.upper() for focus_term in focus_terms):
                        base_confidence *= 1.1
                    
                    term_match = TermMatch(
                        term=term,
                        category=category_name,
                        priority=term_data.get("priority", "medium"),
                        context=context,
                        page_number=page_num,
                        quantities=associated_quantities,
                        confidence=min(1.0, base_confidence)
                    )
                    terms.append(term_match)
        
        return terms
    
    def _term_in_text(self, term: str, text: str) -> bool:
        """Check if a term appears in text (case-insensitive with fuzzy matching)"""
        # Direct match
        if term.lower() in text.lower():
            return True
        
        # Fuzzy match for similar terms
        words = text.upper().split()
        for word in words:
            if fuzz.ratio(term.upper(), word) > 85:  # 85% similarity threshold
                return True
        
        return False
    
    def extract_context(self, text: str, search_term: str, context_size: int) -> str:
        """
        Extract context around a search term
        
        Args:
            text: Full text content
            search_term: Term to search for
            context_size: Number of characters around the term
            
        Returns:
            Extracted context string
        """
        try:
            # Find the term in text (case-insensitive)
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)
            match = pattern.search(text)
            
            if match:
                start = max(0, match.start() - context_size)
                end = min(len(text), match.end() + context_size)
                context = text[start:end]
                
                # Clean up context
                context = context.replace('\n', ' ').strip()
                if len(context) > context_size * 2:
                    context = "..." + context[:context_size] + "..." + context[-context_size:]
                
                return context
            else:
                return search_term
                
        except Exception as e:
            self.logger.warning(f"Error extracting context: {e}")
            return search_term
    
    def _find_associated_quantities(self, term: str, quantities: List[ExtractedQuantity], context: str) -> List[ExtractedQuantity]:
        """Find quantities associated with a specific term"""
        associated = []
        
        for quantity in quantities:
            # Check if quantity appears in the same context
            if quantity.context and term.lower() in quantity.context.lower():
                associated.append(quantity)
            # Check if quantity is on the same line or nearby
            elif abs(quantity.line_number - (context.count('\n') + 1)) <= 2:
                associated.append(quantity)
        
        return associated
    
    def classify_quantity_context(self, context: str) -> str:
        """
        Classify the context of a quantity
        
        Args:
            context: Text context around the quantity
            
        Returns:
            Classification string
        """
        context_lower = context.lower()
        
        # Bridge and railing terms
        if any(term in context_lower for term in ["baluster", "rail", "railing", "bridge"]):
            return "bridge_railing"
        
        # Formwork terms
        if any(term in context_lower for term in ["form", "formwork", "falsework", "blockout"]):
            return "formwork"
        
        # Concrete terms
        if any(term in context_lower for term in ["concrete", "retaining", "wall", "stamped"]):
            return "concrete"
        
        # Temporary structures
        if any(term in context_lower for term in ["erosion", "cribbing", "temporary"]):
            return "temporary_structures"
        
        return "general"
    
    def _generate_alerts(self, terms: List[TermMatch], quantities: List[ExtractedQuantity], page_num: int) -> List[Alert]:
        """Generate alerts based on terms and quantities"""
        alerts = []
        
        # Check for high-priority terms
        for term in terms:
            if term.term in self.high_priority_terms:
                alerts.append(Alert(
                    level=AlertLevel.HIGH,
                    message=f"High-priority term detected: {term.term}",
                    term=term.term,
                    page_number=page_num,
                    details={"category": term.category, "priority": term.priority}
                ))
        
        # Check for large quantities
        for quantity in quantities:
            threshold = self._get_quantity_threshold(quantity.unit)
            if quantity.value > threshold:
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    message=f"Large quantity detected: {quantity.value} {quantity.unit}",
                    quantity=quantity,
                    page_number=page_num,
                    details={"threshold": threshold}
                ))
        
        return alerts
    
    def _get_quantity_threshold(self, unit: str) -> float:
        """Get threshold for large quantity alerts"""
        thresholds = {
            "SQFT": 10000,
            "LF": 5000,
            "CY": 1000,
            "EA": 500,
            "TON": 100,
            "GAL": 10000,
            "LB": 50000
        }
        return thresholds.get(unit, 1000)
    
    def calculate_lumber_requirements(self, terminology: List[TermMatch], quantities: List[ExtractedQuantity]) -> LumberRequirements:
        """
        Calculate lumber requirements based on found terms and quantities
        
        Args:
            terminology: List of found CalTrans terms
            quantities: List of extracted quantities
            
        Returns:
            LumberRequirements with calculated values
        """
        lumber_req = LumberRequirements()
        
        # Calculate formwork area
        formwork_quantities = [
            q for q in quantities 
            if q.unit == "SQFT" and self.classify_quantity_context(q.context) == "formwork"
        ]
        
        total_formwork_area = sum(q.value for q in formwork_quantities)
        lumber_req.formwork_area = total_formwork_area
        
        # Calculate plywood requirements
        lumber_req.plywood_sheets = total_formwork_area * self.lumber_constants["plywood_sheets_per_sqft"]
        lumber_req.plywood_sheets *= (1 + lumber_req.waste_factor) / lumber_req.reuse_factor
        
        # Calculate dimensional lumber
        for size, rate in self.lumber_constants["dimensional_lumber_rates"].items():
            # Estimate based on formwork area and typical usage
            estimated_lf = total_formwork_area * 0.1  # 10% of area as linear feet
            board_feet = estimated_lf * rate
            lumber_req.dimensional_lumber[size] = board_feet * (1 + lumber_req.waste_factor)
        
        # Calculate total board feet
        lumber_req.total_board_feet = sum(lumber_req.dimensional_lumber.values())
        
        # Calculate estimated cost
        plywood_cost = lumber_req.plywood_sheets * self.lumber_constants["material_costs"]["plywood_per_sheet"]
        lumber_cost = lumber_req.total_board_feet * self.lumber_constants["material_costs"]["dimensional_lumber_per_bf"]
        labor_cost = total_formwork_area * self.lumber_constants["material_costs"]["formwork_labor_per_sqft"]
        
        lumber_req.estimated_cost = plywood_cost + lumber_cost + labor_cost
        
        return lumber_req
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calculate text extraction quality score"""
        if not text:
            return 0.0
        
        # Check for common PDF extraction issues
        issues = 0
        total_checks = 4
        
        # Check for excessive whitespace
        if text.count('  ') > len(text) * 0.1:
            issues += 1
        
        # Check for broken words
        if text.count('- ') > len(text) * 0.05:
            issues += 1
        
        # Check for missing punctuation
        if text.count('.') < len(text.split()) * 0.1:
            issues += 1
        
        # Check for garbled characters
        garbled_chars = sum(1 for c in text if ord(c) > 127 and not c.isalpha())
        if garbled_chars > len(text) * 0.1:
            issues += 1
        
        quality = 1.0 - (issues / total_checks)
        return max(0.0, min(1.0, quality))
    
    def _setup_document_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Setup document-specific analysis strategies"""
        return {
            "specifications": {
                "focus_terms": ["MATERIAL", "SPECIFICATION", "STANDARD", "REQUIREMENT", "COMPLIANCE"],
                "quantity_patterns": ["material_specs", "standards", "requirements"],
                "confidence_boost": 1.2,  # Higher confidence for specifications
                "extraction_priority": "high"
            },
            "bid_forms": {
                "focus_terms": ["ITEM", "QUANTITY", "UNIT", "PRICE", "TOTAL", "BID"],
                "quantity_patterns": ["precise_quantities", "pricing", "line_items"],
                "confidence_boost": 1.0,
                "extraction_priority": "critical"
            },
            "construction_plans": {
                "focus_terms": ["DIMENSION", "AREA", "LENGTH", "WIDTH", "HEIGHT", "DETAIL"],
                "quantity_patterns": ["dimensions", "areas", "volumes"],
                "confidence_boost": 0.9,
                "extraction_priority": "medium"
            },
            "supplemental": {
                "focus_terms": ["MODIFICATION", "ADDENDUM", "CHANGE", "SPECIAL", "ADDITIONAL"],
                "quantity_patterns": ["modifications", "changes", "additions"],
                "confidence_boost": 0.8,
                "extraction_priority": "low"
            },
            "general": {
                "focus_terms": ["CONSTRUCTION", "MATERIAL", "QUANTITY", "SPECIFICATION"],
                "quantity_patterns": ["general", "mixed"],
                "confidence_boost": 1.0,
                "extraction_priority": "medium"
            }
        }
    
    def _compile_bid_form_patterns(self) -> Dict[str, re.Pattern]:
        """Compile patterns for extracting bid line items"""
        return {
            "item_number": re.compile(r"(\d+\.?\d*)\s*[A-Z]?", re.IGNORECASE),
            "description": re.compile(r"([A-Z][A-Z\s\d\-\.]+(?:[A-Z][A-Z\s\d\-\.]+)*)", re.IGNORECASE),
            "quantity": re.compile(r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*([A-Z]{2,4})", re.IGNORECASE),
            "unit_price": re.compile(r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE),
            "total_price": re.compile(r"\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*$", re.IGNORECASE),
            "caltrans_code": re.compile(r"([A-Z]{2,4}\s*\d{3,4}[A-Z]?)", re.IGNORECASE)
        }
    
    def analyze_multiple_files(self, file_paths_dict: Dict[str, str]) -> ComprehensiveAnalysisResult:
        """
        Analyze multiple project documents with comprehensive cross-referencing.
        
        Args:
            file_paths_dict: Dictionary mapping document types to file paths
                {"specifications": path, "bid_forms": path, "plans": path, "supplemental": path}
        
        Returns:
            ComprehensiveAnalysisResult with combined analysis and cross-references
        """
        start_time = datetime.now()
        self.logger.info(f"Starting comprehensive analysis of {len(file_paths_dict)} documents")
        
        # Initialize comprehensive result
        comprehensive_result = ComprehensiveAnalysisResult()
        comprehensive_result.total_documents = len(file_paths_dict)
        
        # Process files in priority order
        priority_order = ["specifications", "bid_forms", "construction_plans", "supplemental"]
        
        for doc_type in priority_order:
            if doc_type in file_paths_dict:
                file_path = file_paths_dict[doc_type]
                self.logger.info(f"Processing {doc_type}: {file_path}")
                
                try:
                    # Analyze individual document
                    result = self.analyze_pdf(file_path, document_type=doc_type)
                    comprehensive_result.individual_results[doc_type] = result
                    
                    # Add source document information to findings
                    for term in result.terminology_found:
                        term.source_document = doc_type
                        comprehensive_result.combined_terms.append(term)
                    
                    for quantity in result.quantities:
                        quantity.source_document = doc_type
                        comprehensive_result.combined_quantities.append(quantity)
                    
                    # Extract bid line items if this is a bid form
                    if doc_type == "bid_forms":
                        bid_items = self.extract_bid_line_items(result)
                        comprehensive_result.bid_line_items.extend(bid_items)
                    
                    self.logger.info(f"Completed {doc_type} analysis: {len(result.terminology_found)} terms, {len(result.quantities)} quantities")
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing {doc_type} document: {e}")
                    comprehensive_result.comprehensive_alerts.append(Alert(
                        level=AlertLevel.ERROR,
                        message=f"Failed to analyze {doc_type} document: {str(e)}",
                        details={"document_type": doc_type, "file_path": file_path}
                    ))
        
        # Perform cross-reference analysis
        if len(comprehensive_result.individual_results) > 1:
            comprehensive_result.cross_references = self.cross_reference_findings(
                comprehensive_result.individual_results
            )
        
        # Generate comprehensive alerts
        comprehensive_result.comprehensive_alerts.extend(
            self._generate_comprehensive_alerts(
                comprehensive_result.individual_results,
                comprehensive_result.cross_references
            )
        )
        
        # Calculate summary statistics
        comprehensive_result.total_terms = len(comprehensive_result.combined_terms)
        comprehensive_result.total_quantities = len(comprehensive_result.combined_quantities)
        comprehensive_result.total_alerts = len(comprehensive_result.comprehensive_alerts)
        
        # Calculate overall confidence
        if comprehensive_result.individual_results:
            total_confidence = sum(result.confidence_score for result in comprehensive_result.individual_results.values())
            comprehensive_result.overall_confidence = total_confidence / len(comprehensive_result.individual_results)
        
        # Calculate processing time
        comprehensive_result.processing_time = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"Comprehensive analysis completed: {comprehensive_result.total_terms} terms, "
                        f"{comprehensive_result.total_quantities} quantities, "
                        f"{comprehensive_result.total_alerts} alerts")
        
        return comprehensive_result
    
    def cross_reference_findings(self, analysis_results_list: List[CalTransAnalysisResult]) -> Dict[str, Any]:
        """
        Compare terminology found across documents and validate quantity consistency.
        
        Args:
            analysis_results_list: List of analysis results from different documents
            
        Returns:
            Dictionary with cross-reference analysis results
        """
        self.logger.info("Starting cross-reference analysis across documents")
        
        cross_ref_result = CrossReferenceResult()
        
        # Extract terms and quantities by document
        terms_by_doc = {}
        quantities_by_doc = {}
        
        for result in analysis_results_list:
            doc_type = result.document_type
            terms_by_doc[doc_type] = [term.term for term in result.terminology_found]
            quantities_by_doc[doc_type] = result.quantities
        
        # Check term consistency across documents
        all_terms = set()
        for terms in terms_by_doc.values():
            all_terms.update(terms)
        
        for term in all_terms:
            found_in = [doc_type for doc_type, terms in terms_by_doc.items() if term in terms]
            if len(found_in) > 1:
                cross_ref_result.term_consistency[term] = found_in
        
        # Check quantity discrepancies between bid forms and other documents
        if "bid_forms" in quantities_by_doc:
            bid_quantities = quantities_by_doc["bid_forms"]
            
            for doc_type, quantities in quantities_by_doc.items():
                if doc_type != "bid_forms":
                    for bid_qty in bid_quantities:
                        for other_qty in quantities:
                            if bid_qty.unit == other_qty.unit:
                                # Check for significant discrepancies (10% threshold)
                                diff_percent = abs(bid_qty.value - other_qty.value) / max(bid_qty.value, other_qty.value) * 100
                                if diff_percent > 10:
                                    cross_ref_result.quantity_discrepancies.append({
                                        "term": bid_qty.term_associated or "Unknown",
                                        "bid_forms_value": bid_qty.value,
                                        "other_doc_value": other_qty.value,
                                        "other_doc_type": doc_type,
                                        "difference_percent": diff_percent,
                                        "unit": bid_qty.unit
                                    })
        
        # Check for missing requirements (terms in specs but not in other docs)
        if "specifications" in terms_by_doc:
            spec_terms = set(terms_by_doc["specifications"])
            for doc_type, terms in terms_by_doc.items():
                if doc_type != "specifications":
                    missing = spec_terms - set(terms)
                    for missing_term in missing:
                        cross_ref_result.missing_requirements.append({
                            "term": missing_term,
                            "required_in": "specifications",
                            "missing_from": doc_type
                        })
        
        # Calculate document coverage analysis
        for result in analysis_results_list:
            doc_type = result.document_type
            cross_ref_result.document_coverage[doc_type] = {
                "pages_analyzed": result.total_pages,
                "terms_found": len(result.terminology_found),
                "quantities_found": len(result.quantities),
                "confidence_score": result.confidence_score,
                "quality_score": result.text_extraction_quality
            }
            cross_ref_result.confidence_scores[doc_type] = result.confidence_score
        
        self.logger.info(f"Cross-reference analysis completed: {len(cross_ref_result.term_consistency)} consistent terms, "
                        f"{len(cross_ref_result.quantity_discrepancies)} discrepancies")
        
        return cross_ref_result
    
    def extract_bid_line_items(self, analysis_result: CalTransAnalysisResult) -> List[BidLineItem]:
        """
        Parse official bid forms for line items.
        
        Args:
            analysis_result: Analysis result from bid forms document
            
        Returns:
            List of structured bid line items
        """
        self.logger.info("Extracting bid line items from bid forms")
        
        bid_items = []
        
        # Extract text from all pages
        full_text = ""
        for sheet_analysis in analysis_result.sheet_analyses:
            full_text += sheet_analysis.text_content + "\n"
        
        # Split into lines for processing
        lines = full_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            try:
                # Look for line item patterns
                item_match = self.bid_form_patterns["item_number"].search(line)
                if not item_match:
                    continue
                
                item_number = item_match.group(1)
                
                # Extract description
                desc_match = self.bid_form_patterns["description"].search(line)
                description = desc_match.group(1) if desc_match else "No description"
                
                # Extract quantity and unit
                qty_match = self.bid_form_patterns["quantity"].search(line)
                if qty_match:
                    quantity = float(qty_match.group(1).replace(',', ''))
                    unit = qty_match.group(2)
                else:
                    quantity = 0.0
                    unit = "EA"
                
                # Extract CalTrans code
                code_match = self.bid_form_patterns["caltrans_code"].search(line)
                caltrans_code = code_match.group(1) if code_match else "N/A"
                
                # Extract unit price
                price_match = self.bid_form_patterns["unit_price"].search(line)
                unit_price = float(price_match.group(1).replace(',', '')) if price_match else None
                
                # Extract total price
                total_match = self.bid_form_patterns["total_price"].search(line)
                total_price = float(total_match.group(1).replace(',', '')) if total_match else None
                
                # Find matching terms from analysis
                term_matches = []
                for term in analysis_result.terminology_found:
                    if term.term.lower() in description.lower():
                        term_matches.append(term.term)
                
                # Calculate confidence based on completeness
                confidence = 1.0
                if not description or description == "No description":
                    confidence *= 0.8
                if not caltrans_code or caltrans_code == "N/A":
                    confidence *= 0.9
                if unit_price is None:
                    confidence *= 0.95
                
                bid_item = BidLineItem(
                    item_number=item_number,
                    description=description,
                    caltrans_code=caltrans_code,
                    quantity=quantity,
                    unit=unit,
                    unit_price=unit_price,
                    total_price=total_price,
                    confidence=confidence,
                    term_matches=term_matches
                )
                
                bid_items.append(bid_item)
                
            except Exception as e:
                self.logger.warning(f"Error parsing bid line item on line {line_num}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(bid_items)} bid line items")
        return bid_items
    
    def _calculate_confidence_score(self, result: CalTransAnalysisResult) -> float:
        """
        Calculate confidence score for analysis results.
        
        Args:
            result: Analysis result to evaluate
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence on text extraction quality
        confidence = result.text_extraction_quality
        
        # Boost confidence for high-priority terms found
        if result.high_priority_terms > 0:
            confidence += min(0.2, result.high_priority_terms * 0.05)
        
        # Boost confidence for quantities found
        if result.total_quantities > 0:
            confidence += min(0.1, result.total_quantities * 0.01)
        
        # Reduce confidence for critical alerts
        if result.critical_alerts > 0:
            confidence -= min(0.3, result.critical_alerts * 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    def _cross_reference_findings(self, individual_results: Dict[str, CalTransAnalysisResult]) -> Dict[str, Any]:
        """Cross-reference findings between different documents"""
        
        cross_refs = {
            'term_matches': [],
            'quantity_discrepancies': [],
            'missing_requirements': [],
            'document_coverage': {}
        }
        
        # Extract all terms and quantities by category
        terms_by_category = {}
        quantities_by_category = {}
        
        for category, result in individual_results.items():
            terms_by_category[category] = [term.term for term in result.terminology_found]
            quantities_by_category[category] = result.quantities
        
        # Check for term matches across documents
        all_terms = set()
        for terms in terms_by_category.values():
            all_terms.update(terms)
        
        for term in all_terms:
            found_in = [cat for cat, terms in terms_by_category.items() if term in terms]
            if len(found_in) > 1:
                cross_refs['term_matches'].append({
                    'term': term,
                    'found_in': found_in,
                    'consistency': 'high' if len(found_in) == len(individual_results) else 'partial'
                })
        
        # Check for quantity discrepancies
        if 'specifications' in quantities_by_category and 'bid_forms' in quantities_by_category:
            spec_quantities = quantities_by_category['specifications']
            bid_quantities = quantities_by_category['bid_forms']
            
            for spec_qty in spec_quantities:
                for bid_qty in bid_quantities:
                    if (spec_qty.unit == bid_qty.unit and 
                        abs(spec_qty.value - bid_qty.value) / max(spec_qty.value, 1) > 0.1):  # 10% threshold
                        cross_refs['quantity_discrepancies'].append({
                            'specification_value': spec_qty.value,
                            'bid_form_value': bid_qty.value,
                            'unit': spec_qty.unit,
                            'difference_percent': abs(spec_qty.value - bid_qty.value) / spec_qty.value * 100
                        })
        
        # Check for missing requirements
        if 'specifications' in individual_results:
            spec_terms = set(terms_by_category.get('specifications', []))
            for category, terms in terms_by_category.items():
                if category != 'specifications':
                    missing = spec_terms - set(terms)
                    if missing:
                        cross_refs['missing_requirements'].append({
                            'category': category,
                            'missing_terms': list(missing)
                        })
        
        # Document coverage analysis
        for category, result in individual_results.items():
            cross_refs['document_coverage'][category] = {
                'pages_analyzed': result.total_pages,
                'terms_found': len(result.terminology_found),
                'quantities_found': len(result.quantities),
                'confidence_score': result.confidence_score,
                'quality_score': result.text_extraction_quality
            }
        
        return cross_refs
    
    def _generate_comprehensive_alerts(self, individual_results: Dict[str, CalTransAnalysisResult], 
                                     cross_references: Dict[str, Any]) -> List[Alert]:
        """Generate comprehensive alerts based on cross-referenced findings"""
        
        alerts = []
        
        # Check for quantity discrepancies
        for discrepancy in cross_references.get('quantity_discrepancies', []):
            alerts.append(Alert(
                level=AlertLevel.HIGH,
                message=f"Quantity discrepancy detected: {discrepancy['specification_value']} vs {discrepancy['bid_form_value']} {discrepancy['unit']} ({discrepancy['difference_percent']:.1f}% difference)",
                details=discrepancy
            ))
        
        # Check for missing requirements
        for missing in cross_references.get('missing_requirements', []):
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                message=f"Missing requirements in {missing['category']}: {', '.join(missing['missing_terms'][:3])}",
                details=missing
            ))
        
        # Check for low confidence scores
        low_confidence_files = [
            (cat, result.confidence_score) 
            for cat, result in individual_results.items() 
            if result.confidence_score < 0.7
        ]
        
        for category, confidence in low_confidence_files:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                message=f"Low confidence analysis for {category}: {confidence:.1%}",
                details={'category': category, 'confidence': confidence}
            ))
        
        # Check for critical terms found
        critical_terms_found = []
        for category, result in individual_results.items():
            for term in result.terminology_found:
                if term.term in self.high_priority_terms:
                    critical_terms_found.append({
                        'term': term.term,
                        'category': category,
                        'priority': term.priority
                    })
        
        if critical_terms_found:
            alerts.append(Alert(
                level=AlertLevel.INFO,
                message=f"Critical terms found: {', '.join([t['term'] for t in critical_terms_found[:5]])}",
                details={'critical_terms': critical_terms_found}
            ))
        
        return alerts


# Utility functions for external use
def analyze_caltrans_pdf(pdf_path: str) -> CalTransAnalysisResult:
    """Convenience function for PDF analysis"""
    analyzer = CalTransPDFAnalyzer()
    return analyzer.analyze_pdf(pdf_path)


def extract_quantities_from_text(text: str) -> List[ExtractedQuantity]:
    """Convenience function for quantity extraction"""
    analyzer = CalTransPDFAnalyzer()
    return analyzer._extract_quantities(text, 1)


def find_caltrans_terms(text: str) -> List[TermMatch]:
    """Convenience function for term detection"""
    analyzer = CalTransPDFAnalyzer()
    return analyzer._find_caltrans_terms(text, 1, [])


if __name__ == "__main__":
    # Example usage
    analyzer = CalTransPDFAnalyzer()
    
    # Test with a sample PDF
    test_pdf = "sample_caltrans_project.pdf"
    if os.path.exists(test_pdf):
        result = analyzer.analyze_pdf(test_pdf)
        print(f"Analysis completed: {len(result.terminology_found)} terms found")
        print(f"Quantities extracted: {len(result.quantities)}")
        print(f"Alerts generated: {len(result.alerts)}")
        print(f"Lumber requirements: {result.total_lumber_requirements.total_board_feet:.2f} board feet")
    else:
        print("Test PDF not found. Run with actual CalTrans PDF for testing.") 