"""
Multi-File Upload Component for PACE Bid Generation

This module provides a professional multi-file upload interface for the bid generation
page, supporting categorized file uploads with validation, progress tracking, and
comprehensive analysis workflow.

Features:
- Categorized file uploads (Specs, Bid Forms, Plans, Supplemental)
- Drag-and-drop functionality
- Progress tracking for each file
- Validation and error handling
- Professional UI with PACE branding
- Session state management for multiple files
"""

import streamlit as st
import os
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum


class FileCategory(Enum):
    """File categories for bid generation"""
    SPECIFICATIONS = "specifications"
    BID_FORMS = "bid_forms"
    CONSTRUCTION_PLANS = "construction_plans"
    SUPPLEMENTAL = "supplemental"


class FileStatus(Enum):
    """File processing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    VALIDATED = "validated"


@dataclass
class UploadedFile:
    """Represents an uploaded file with metadata"""
    name: str
    category: FileCategory
    file_data: bytes
    size: int
    upload_time: datetime
    status: FileStatus = FileStatus.PENDING
    processing_time: float = 0.0
    analysis_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    confidence_score: float = 0.0
    terms_found: List[str] = field(default_factory=list)
    quantities_found: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session state storage"""
        return {
            "name": self.name,
            "category": self.category.value,
            "size": self.size,
            "upload_time": self.upload_time.isoformat(),
            "status": self.status.value,
            "processing_time": self.processing_time,
            "analysis_result": self.analysis_result,
            "error_message": self.error_message,
            "confidence_score": self.confidence_score,
            "terms_found": self.terms_found,
            "quantities_found": self.quantities_found
        }


class MultiFileUploadComponent:
    """Professional multi-file upload component for bid generation"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = ['.pdf']
        self.required_categories = [FileCategory.SPECIFICATIONS]
        self.recommended_categories = [FileCategory.BID_FORMS, FileCategory.CONSTRUCTION_PLANS]
        
        # File category configurations
        self.category_configs = {
            FileCategory.SPECIFICATIONS: {
                "icon": "📋",
                "title": "Project Specifications",
                "description": "Contains CalTrans terminology, material specifications, and construction requirements",
                "example": "08-1J5404sp.pdf",
                "required": True,
                "color": "#dc2626"  # Red for required
            },
            FileCategory.BID_FORMS: {
                "icon": "💰",
                "title": "Bid Forms",
                "description": "Official bid items list with quantities and unit prices",
                "example": "08-1J5404formsforbid.pdf",
                "required": False,
                "color": "#ea580c"  # Orange for highly recommended
            },
            FileCategory.CONSTRUCTION_PLANS: {
                "icon": "📐",
                "title": "Construction Plans",
                "description": "Technical drawings, dimensions, and visual specifications",
                "example": "08-1J5404plans.pdf",
                "required": False,
                "color": "#2563eb"  # Blue for recommended
            },
            FileCategory.SUPPLEMENTAL: {
                "icon": "📄",
                "title": "Supplemental Information",
                "description": "Additional requirements, special provisions, addendums",
                "example": "08-1J5404-IH.pdf",
                "required": False,
                "color": "#059669"  # Green for optional
            }
        }
    
    def render_upload_section(self) -> Dict[str, Any]:
        """Render the main multi-file upload section"""
        
        # Header
        st.markdown("## 📁 Multi-Document Upload")
        st.markdown("Upload comprehensive project documents for thorough bid analysis and generation.")
        
        # File category upload sections
        uploaded_files = {}
        
        for category in FileCategory:
            config = self.category_configs[category]
            uploaded_file = self._render_category_upload(category, config)
            if uploaded_file:
                uploaded_files[category] = uploaded_file
        
        # Validation and processing
        if uploaded_files:
            return self._process_uploaded_files(uploaded_files)
        
        return {}
    
    def _render_category_upload(self, category: FileCategory, config: Dict[str, Any]) -> Optional[UploadedFile]:
        """Render upload section for a specific category"""
        
        # Create styled container
        with st.container():
            # Category header with styling
            st.markdown(f"""
            <div style="
                border: 2px solid {config['color']};
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                background: linear-gradient(135deg, {config['color']}15 0%, {config['color']}05 100%);
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2rem; margin-right: 1rem;">{config['icon']}</span>
                    <div>
                        <h3 style="margin: 0; color: {config['color']}; font-weight: 600;">
                            {config['title']}
                            {' <span style="color: #dc2626;">(Required)</span>' if config['required'] else ' <span style="color: #ea580c;">(Recommended)</span>' if category in self.recommended_categories else ' <span style="color: #059669;">(Optional)</span>'}
                        </h3>
                        <p style="margin: 0.5rem 0; color: #6b7280; font-size: 0.9rem;">
                            {config['description']}
                        </p>
                        <p style="margin: 0; color: #9ca3af; font-size: 0.8rem; font-style: italic;">
                            Example: {config['example']}
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # File upload widget
            uploaded_file = st.file_uploader(
                f"Upload {config['title']}",
                type=['pdf'],
                key=f"upload_{category.value}",
                help=f"Upload {config['title'].lower()} file (PDF format)"
            )
            
            if uploaded_file:
                # Validate and process file
                validation_result = self._validate_file(uploaded_file)
                
                if validation_result['valid']:
                    # Create UploadedFile object
                    uploaded_file_obj = UploadedFile(
                        name=uploaded_file.name,
                        category=category,
                        file_data=uploaded_file.read(),
                        size=uploaded_file.size,
                        upload_time=datetime.now(),
                        status=FileStatus.UPLOADING
                    )
                    
                    # Display file info
                    self._display_file_info(uploaded_file_obj, validation_result)
                    
                    return uploaded_file_obj
                else:
                    st.error(f"❌ {validation_result['error']}")
        
        return None
    
    def _validate_file(self, uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file"""
        
        # Check file size
        if uploaded_file.size > self.max_file_size:
            return {
                'valid': False,
                'error': f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (50MB)"
            }
        
        # Check file extension
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return {
                'valid': False,
                'error': f"File type '{file_ext}' not supported. Please upload PDF files only."
            }
        
        # Check if file is readable
        try:
            uploaded_file.seek(0)
            return {'valid': True, 'file_size_mb': uploaded_file.size / 1024 / 1024}
        except Exception as e:
            return {
                'valid': False,
                'error': f"Unable to read file: {str(e)}"
            }
    
    def _display_file_info(self, uploaded_file: UploadedFile, validation_result: Dict[str, Any]):
        """Display file information"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Size", f"{validation_result['file_size_mb']:.1f} MB")
        
        with col2:
            st.metric("Category", uploaded_file.category.value.replace('_', ' ').title())
        
        with col3:
            st.metric("Status", "✅ Ready for Analysis")
        
        st.success(f"📄 **{uploaded_file.name}** uploaded successfully!")
    
    def _process_uploaded_files(self, uploaded_files: Dict[FileCategory, UploadedFile]) -> Dict[str, Any]:
        """Process all uploaded files and return analysis results"""
        
        st.markdown("---")
        st.markdown("## 🔍 Document Analysis")
        
        # Check required files
        missing_required = [cat for cat in self.required_categories if cat not in uploaded_files]
        if missing_required:
            st.error(f"❌ Missing required files: {', '.join([cat.value for cat in missing_required])}")
            return {}
        
        # Process files in priority order
        processing_order = [
            FileCategory.SPECIFICATIONS,
            FileCategory.BID_FORMS,
            FileCategory.CONSTRUCTION_PLANS,
            FileCategory.SUPPLEMENTAL
        ]
        
        analysis_results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, category in enumerate(processing_order):
            if category in uploaded_files:
                file_obj = uploaded_files[category]
                
                # Update progress
                progress = (i + 1) / len([cat for cat in processing_order if cat in uploaded_files])
                progress_bar.progress(progress)
                status_text.text(f"Analyzing {file_obj.name}...")
                
                # Process file
                result = self._analyze_file(file_obj)
                analysis_results[category.value] = result
                
                # Update file status
                file_obj.status = FileStatus.COMPLETED if result['success'] else FileStatus.ERROR
                file_obj.analysis_result = result
                file_obj.processing_time = result.get('processing_time', 0)
                file_obj.confidence_score = result.get('confidence_score', 0)
                file_obj.terms_found = result.get('terms_found', [])
                file_obj.quantities_found = result.get('quantities_found', [])
        
        progress_bar.progress(1.0)
        status_text.text("✅ Analysis complete!")
        
        # Display analysis summary
        self._display_analysis_summary(analysis_results)
        
        # Store in session state
        self._store_analysis_results(analysis_results, uploaded_files)
        
        return analysis_results
    
    def _analyze_file(self, file_obj: UploadedFile) -> Dict[str, Any]:
        """Analyze a single file using CalTrans analyzer"""
        
        try:
            # Import analyzer here to avoid circular imports
            from src.analyzers.caltrans_analyzer import CalTransPDFAnalyzer
            
            # Create temporary file for analysis
            temp_path = Path("data/temp") / f"temp_{file_obj.name}"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(file_obj.file_data)
            
            # Analyze file
            analyzer = CalTransPDFAnalyzer()
            result = analyzer.analyze_pdf(str(temp_path))
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            return {
                'success': True,
                'processing_time': result.processing_time,
                'confidence_score': result.confidence_score,
                'terms_found': [term.term for term in result.terminology_found],
                'quantities_found': [
                    {
                        'value': q.value,
                        'unit': q.unit,
                        'context': q.context
                    } for q in result.quantities
                ],
                'total_pages': result.total_pages,
                'high_priority_terms': result.high_priority_terms,
                'total_quantities': result.total_quantities,
                'critical_alerts': result.critical_alerts,
                'alerts': [
                    {
                        'level': alert.level.value,
                        'message': alert.message
                    } for alert in result.alerts
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0,
                'confidence_score': 0
            }
    
    def _display_analysis_summary(self, analysis_results: Dict[str, Any]):
        """Display analysis summary"""
        
        st.markdown("### 📊 Analysis Summary")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_terms = sum(len(result.get('terms_found', [])) for result in analysis_results.values())
        total_quantities = sum(len(result.get('quantities_found', [])) for result in analysis_results.values())
        total_alerts = sum(len(result.get('alerts', [])) for result in analysis_results.values())
        avg_confidence = sum(result.get('confidence_score', 0) for result in analysis_results.values()) / len(analysis_results) if analysis_results else 0
        
        with col1:
            st.metric("Documents Analyzed", len(analysis_results))
        
        with col2:
            st.metric("Terms Found", total_terms)
        
        with col3:
            st.metric("Quantities Extracted", total_quantities)
        
        with col4:
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        
        # Document-specific results
        st.markdown("#### 📋 Document Analysis Results")
        
        for category, result in analysis_results.items():
            if result['success']:
                with st.expander(f"📄 {category.replace('_', ' ').title()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Terms Found:** {len(result.get('terms_found', []))}")
                        st.write(f"**Quantities:** {len(result.get('quantities_found', []))}")
                        st.write(f"**Processing Time:** {result.get('processing_time', 0):.2f}s")
                    
                    with col2:
                        st.write(f"**Confidence:** {result.get('confidence_score', 0):.1%}")
                        st.write(f"**Pages:** {result.get('total_pages', 0)}")
                        st.write(f"**Alerts:** {len(result.get('alerts', []))}")
                    
                    # Show sample terms and quantities
                    if result.get('terms_found'):
                        st.write("**Sample Terms:**")
                        st.write(", ".join(result['terms_found'][:5]))
                    
                    if result.get('quantities_found'):
                        st.write("**Sample Quantities:**")
                        for qty in result['quantities_found'][:3]:
                            st.write(f"- {qty['value']} {qty['unit']} ({qty['context'][:50]}...)")
            else:
                st.error(f"❌ Failed to analyze {category}: {result.get('error', 'Unknown error')}")
    
    def _store_analysis_results(self, analysis_results: Dict[str, Any], uploaded_files: Dict[FileCategory, UploadedFile]):
        """Store analysis results in session state"""
        
        # Store uploaded files
        st.session_state.uploaded_files = {
            category.value: file_obj.to_dict() 
            for category, file_obj in uploaded_files.items()
        }
        
        # Store analysis results
        st.session_state.multi_file_analysis = analysis_results
        
        # Store combined results for bid generation
        combined_terms = []
        combined_quantities = []
        combined_alerts = []
        
        for result in analysis_results.values():
            if result['success']:
                combined_terms.extend(result.get('terms_found', []))
                combined_quantities.extend(result.get('quantities_found', []))
                combined_alerts.extend(result.get('alerts', []))
        
        st.session_state.combined_analysis = {
            'total_documents': len(analysis_results),
            'total_terms': len(combined_terms),
            'total_quantities': len(combined_quantities),
            'total_alerts': len(combined_alerts),
            'terms': combined_terms,
            'quantities': combined_quantities,
            'alerts': combined_alerts,
            'analysis_timestamp': datetime.now().isoformat()
        }


def render_multi_file_upload() -> Dict[str, Any]:
    """Render the multi-file upload component"""
    component = MultiFileUploadComponent()
    return component.render_upload_section()


def get_upload_status() -> Dict[str, Any]:
    """Get current upload and analysis status"""
    return {
        'has_uploaded_files': 'uploaded_files' in st.session_state,
        'has_analysis': 'multi_file_analysis' in st.session_state,
        'file_count': len(st.session_state.get('uploaded_files', {})),
        'analysis_complete': 'combined_analysis' in st.session_state
    } 