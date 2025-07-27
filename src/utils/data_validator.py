"""
Data Validation Utilities for CalTrans Bidding System

This module provides comprehensive validation functions for:
- PDF file uploads and processing
- Data quality assessment
- CalTrans terminology validation
- Error handling and logging
- File cleanup utilities
- Progress tracking
"""

import os
import sys
import json
import logging
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import (
    Dict, List, Tuple, Optional, Union, Any, Callable,
    Generator, Set, NamedTuple
)
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Third-party imports
import pdfplumber
import pandas as pd
from PIL import Image
import magic

# Local imports
from config.settings import get_setting


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FileType(Enum):
    """Supported file types"""
    PDF = "application/pdf"
    IMAGE = "image/"
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JSON = "application/json"
    TEXT = "text/plain"


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    level: ValidationLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    page_number: Optional[int] = None


@dataclass
class ProgressTracker:
    """Progress tracking for long-running operations"""
    total_items: int
    current_item: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    completed_items: Set[str] = field(default_factory=set)
    failed_items: Set[str] = field(default_factory=set)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def update(self, item_id: str, success: bool = True, message: str = "") -> None:
        """Update progress for an item"""
        self.current_item += 1
        self.last_update = datetime.now()
        
        if success:
            self.completed_items.add(item_id)
        else:
            self.failed_items.add(item_id)
            self.errors.append(f"Item {item_id}: {message}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress statistics"""
        elapsed = datetime.now() - self.start_time
        completion_rate = (self.current_item / self.total_items) * 100 if self.total_items > 0 else 0
        
        if self.current_item > 0:
            estimated_total = elapsed * (self.total_items / self.current_item)
            eta = self.start_time + estimated_total
        else:
            eta = None
        
        return {
            "current_item": self.current_item,
            "total_items": self.total_items,
            "completion_rate": completion_rate,
            "elapsed_time": str(elapsed),
            "eta": eta.isoformat() if eta else None,
            "completed_count": len(self.completed_items),
            "failed_count": len(self.failed_items),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors)
        }


class DataValidator:
    """Main data validation class"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the data validator"""
        self.logger = logger or self._setup_logger()
        self.settings = get_setting()
        self.temp_dir = Path(tempfile.gettempdir()) / "caltrans_bidding"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Load CalTrans reference data
        self.caltrans_reference = self._load_caltrans_reference()
        
        # Validation cache
        self._validation_cache: Dict[str, ValidationResult] = {}
        self._cache_ttl = timedelta(hours=1)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for validation operations"""
        logger = logging.getLogger("data_validator")
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
            reference_path = Path("data/caltrans_reference.json")
            if reference_path.exists():
                with open(reference_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning("CalTrans reference file not found")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading CalTrans reference: {e}")
            return {}
    
    def validate_pdf_upload(
        self, 
        file_path: Union[str, Path], 
        check_content: bool = True
    ) -> ValidationResult:
        """
        Validate PDF file upload
        
        Args:
            file_path: Path to the PDF file
            check_content: Whether to validate PDF content readability
            
        Returns:
            ValidationResult with validation status and details
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"File does not exist: {file_path}",
                file_path=str(file_path)
            )
        
        # Check file size
        file_size = file_path.stat().st_size
        max_size = self.settings.get('FILE_UPLOAD_CONFIG', {}).get('max_file_size', 100 * 1024 * 1024)
        
        if file_size > max_size:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"File size {file_size} exceeds maximum {max_size}",
                details={"file_size": file_size, "max_size": max_size},
                file_path=str(file_path)
            )
        
        # Check file type
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type != FileType.PDF.value:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid file type: {mime_type}, expected PDF",
                    details={"mime_type": mime_type},
                    file_path=str(file_path)
                )
        except Exception as e:
            self.logger.warning(f"Could not determine MIME type: {e}")
        
        # Check PDF content if requested
        if check_content:
            content_result = self._validate_pdf_content(file_path)
            if not content_result.is_valid:
                return content_result
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="PDF file validation successful",
            details={
                "file_size": file_size,
                "pages": self._get_pdf_page_count(file_path),
                "mime_type": mime_type
            },
            file_path=str(file_path)
        )
    
    def _validate_pdf_content(self, file_path: Path) -> ValidationResult:
        """Validate PDF content readability"""
        try:
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.ERROR,
                        message="PDF has no pages",
                        file_path=str(file_path)
                    )
                
                # Check first few pages for text extraction
                text_pages = 0
                total_pages = min(5, len(pdf.pages))
                
                for i in range(total_pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:  # Minimum text threshold
                        text_pages += 1
                
                if text_pages == 0:
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.WARNING,
                        message="PDF appears to be image-based or unreadable",
                        details={"total_pages": len(pdf.pages), "text_pages": text_pages},
                        file_path=str(file_path)
                    )
                
                return ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.INFO,
                    message=f"PDF content validation successful ({text_pages}/{total_pages} pages readable)",
                    details={"total_pages": len(pdf.pages), "text_pages": text_pages},
                    file_path=str(file_path)
                )
                
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Error reading PDF content: {str(e)}",
                file_path=str(file_path)
            )
    
    def _get_pdf_page_count(self, file_path: Path) -> int:
        """Get PDF page count"""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0
    
    def validate_product_data(
        self, 
        product_data: Dict[str, Any], 
        required_fields: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate extracted product data quality
        
        Args:
            product_data: Dictionary containing product information
            required_fields: List of required fields to check
            
        Returns:
            ValidationResult with validation status
        """
        if not isinstance(product_data, dict):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Product data must be a dictionary"
            )
        
        # Default required fields
        if required_fields is None:
            required_fields = ["name", "price", "sku"]
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in product_data]
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Missing required fields: {missing_fields}",
                details={"missing_fields": missing_fields}
            )
        
        # Validate data types and formats
        validation_errors = []
        
        # Check price
        if "price" in product_data:
            try:
                price = float(product_data["price"])
                if price < 0:
                    validation_errors.append("Price cannot be negative")
            except (ValueError, TypeError):
                validation_errors.append("Invalid price format")
        
        # Check SKU
        if "sku" in product_data:
            sku = str(product_data["sku"]).strip()
            if not sku:
                validation_errors.append("SKU cannot be empty")
        
        # Check name
        if "name" in product_data:
            name = str(product_data["name"]).strip()
            if len(name) < 3:
                validation_errors.append("Product name too short")
        
        if validation_errors:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Product data validation failed",
                details={"errors": validation_errors}
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Product data validation successful"
        )
    
    def validate_caltrans_terminology(
        self, 
        extracted_text: str, 
        context: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate CalTrans terminology extraction
        
        Args:
            extracted_text: Text containing potential CalTrans terms
            context: Context information (e.g., section, page)
            
        Returns:
            ValidationResult with validation status
        """
        if not self.caltrans_reference:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="CalTrans reference data not available"
            )
        
        # Extract potential terms
        found_terms = []
        missing_terms = []
        low_confidence_terms = []
        
        # Check bridge and barrier terms
        bridge_terms = self.caltrans_reference.get("bridge_barrier_terms", {})
        for term, data in bridge_terms.items():
            if self._term_in_text(term, extracted_text):
                found_terms.append({
                    "term": term,
                    "category": "bridge_barrier",
                    "priority": data.get("priority", "medium")
                })
        
        # Check formwork terms
        formwork_terms = self.caltrans_reference.get("formwork_terms", {})
        for term, data in formwork_terms.items():
            if self._term_in_text(term, extracted_text):
                found_terms.append({
                    "term": term,
                    "category": "formwork",
                    "priority": data.get("priority", "medium")
                })
        
        # Check concrete terms
        concrete_terms = self.caltrans_reference.get("concrete_terms", {})
        for term, data in concrete_terms.items():
            if self._term_in_text(term, extracted_text):
                found_terms.append({
                    "term": term,
                    "category": "concrete",
                    "priority": data.get("priority", "medium")
                })
        
        # Analyze results
        critical_terms = [t for t in found_terms if t["priority"] == "critical"]
        high_priority_terms = [t for t in found_terms if t["priority"] == "high"]
        
        if not found_terms:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="No CalTrans terminology found in text",
                details={"context": context}
            )
        
        # Check for critical terms
        if critical_terms:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"Found {len(critical_terms)} critical CalTrans terms",
                details={
                    "found_terms": found_terms,
                    "critical_count": len(critical_terms),
                    "high_priority_count": len(high_priority_terms),
                    "context": context
                }
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Found {len(found_terms)} CalTrans terms",
            details={
                "found_terms": found_terms,
                "high_priority_count": len(high_priority_terms),
                "context": context
            }
        )
    
    def _term_in_text(self, term: str, text: str) -> bool:
        """Check if a term appears in text (case-insensitive)"""
        return term.lower() in text.lower()
    
    def validate_quantity_extraction(
        self, 
        extracted_quantities: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        Validate quantity extraction results
        
        Args:
            extracted_quantities: List of extracted quantities
            
        Returns:
            ValidationResult with validation status
        """
        if not isinstance(extracted_quantities, list):
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Extracted quantities must be a list"
            )
        
        validation_errors = []
        valid_quantities = []
        
        for i, quantity in enumerate(extracted_quantities):
            if not isinstance(quantity, dict):
                validation_errors.append(f"Quantity {i}: Must be a dictionary")
                continue
            
            # Check required fields
            required = ["value", "unit"]
            missing = [field for field in required if field not in quantity]
            if missing:
                validation_errors.append(f"Quantity {i}: Missing fields {missing}")
                continue
            
            # Validate value
            try:
                value = float(quantity["value"])
                if value <= 0:
                    validation_errors.append(f"Quantity {i}: Value must be positive")
                    continue
            except (ValueError, TypeError):
                validation_errors.append(f"Quantity {i}: Invalid value format")
                continue
            
            # Validate unit
            unit = str(quantity["unit"]).upper()
            valid_units = ["SQFT", "LF", "CY", "EA", "TON", "GAL", "LB"]
            if unit not in valid_units:
                validation_errors.append(f"Quantity {i}: Invalid unit {unit}")
                continue
            
            valid_quantities.append(quantity)
        
        if validation_errors:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Quantity extraction validation failed",
                details={"errors": validation_errors}
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Quantity extraction validation successful ({len(valid_quantities)} valid quantities)",
            details={"valid_count": len(valid_quantities), "total_count": len(extracted_quantities)}
        )
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> ValidationResult:
        """
        Clean up temporary files older than specified age
        
        Args:
            max_age_hours: Maximum age of files to keep
            
        Returns:
            ValidationResult with cleanup status
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            deleted_count = 0
            error_count = 0
            
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        if file_path.stat().st_mtime < cutoff_time.timestamp():
                            file_path.unlink()
                            deleted_count += 1
                    except Exception as e:
                        error_count += 1
                        self.logger.error(f"Error deleting {file_path}: {e}")
            
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"Cleanup completed: {deleted_count} files deleted, {error_count} errors",
                details={"deleted_count": deleted_count, "error_count": error_count}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Cleanup failed: {str(e)}"
            )
    
    def create_progress_tracker(self, total_items: int) -> ProgressTracker:
        """Create a new progress tracker"""
        return ProgressTracker(total_items=total_items)
    
    def log_validation_result(self, result: ValidationResult) -> None:
        """Log validation result with appropriate level"""
        log_message = f"{result.message} - {result.details}"
        
        if result.level == ValidationLevel.INFO:
            self.logger.info(log_message)
        elif result.level == ValidationLevel.WARNING:
            self.logger.warning(log_message)
        elif result.level == ValidationLevel.ERROR:
            self.logger.error(log_message)
        elif result.level == ValidationLevel.CRITICAL:
            self.logger.critical(log_message)
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate summary of validation results"""
        summary = {
            "total_validations": len(results),
            "valid_count": sum(1 for r in results if r.is_valid),
            "invalid_count": sum(1 for r in results if not r.is_valid),
            "by_level": {},
            "errors": [],
            "warnings": []
        }
        
        for result in results:
            level = result.level.value
            if level not in summary["by_level"]:
                summary["by_level"][level] = 0
            summary["by_level"][level] += 1
            
            if not result.is_valid:
                if result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
                    summary["errors"].append(result.message)
                elif result.level == ValidationLevel.WARNING:
                    summary["warnings"].append(result.message)
        
        return summary


# Utility functions for external use
def validate_file_upload(file_path: Union[str, Path]) -> ValidationResult:
    """Convenience function for file upload validation"""
    validator = DataValidator()
    return validator.validate_pdf_upload(file_path)


def validate_product_extraction(product_data: Dict[str, Any]) -> ValidationResult:
    """Convenience function for product data validation"""
    validator = DataValidator()
    return validator.validate_product_data(product_data)


def validate_caltrans_extraction(text: str, context: str = None) -> ValidationResult:
    """Convenience function for CalTrans terminology validation"""
    validator = DataValidator()
    return validator.validate_caltrans_terminology(text, context)


def cleanup_old_files(max_age_hours: int = 24) -> ValidationResult:
    """Convenience function for file cleanup"""
    validator = DataValidator()
    return validator.cleanup_temp_files(max_age_hours)


# Error handling decorators
def handle_validation_errors(func: Callable) -> Callable:
    """Decorator to handle validation errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger("data_validator")
            logger.error(f"Validation error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Validation failed: {str(e)}",
                details={"function": func.__name__, "error": str(e)}
            )
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry operations on failure"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            # If all retries failed, raise the last exception
            raise last_exception
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    validator = DataValidator()
    
    # Test PDF validation
    test_pdf = Path("test.pdf")
    if test_pdf.exists():
        result = validator.validate_pdf_upload(test_pdf)
        validator.log_validation_result(result)
    
    # Test product validation
    test_product = {
        "name": "Test Product",
        "price": 100.0,
        "sku": "TEST123"
    }
    result = validator.validate_product_data(test_product)
    validator.log_validation_result(result)
    
    # Test CalTrans validation
    test_text = "BALUSTER TYPE_86H_RAIL concrete forming"
    result = validator.validate_caltrans_terminology(test_text)
    validator.log_validation_result(result) 