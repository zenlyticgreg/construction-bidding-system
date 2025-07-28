"""
File Upload Components for PACE - Project Analysis & Construction Estimating

This module provides file upload and processing components for the PACE
construction bidding automation platform, supporting multiple file formats
and batch processing capabilities.

The upload components support:
- Multi-format file upload (PDF, Excel, Word, etc.)
- Drag-and-drop functionality
- Progress tracking and status updates
- File validation and error handling
- Batch processing capabilities
- File history and management

For more information, visit: https://pace-construction.com
"""

import streamlit as st
import os
import hashlib
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import pdfplumber
import pandas as pd


class FileUploadComponent:
    """Component for handling PDF file uploads with validation and progress tracking."""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = ['.pdf']
        self.uploaded_files = []
        
    def render_upload_section(self) -> Optional[Dict[str, Any]]:
        """
        Render the main file upload section.
        
        Returns:
            Dict containing file data and metadata if upload successful, None otherwise
        """
        st.header("📄 Upload CalTrans Documents")
        st.markdown("Upload PDF files containing CalTrans specifications and requirements.")
        
        # Add a container to prevent layout shifts
        upload_container = st.container()
        
        with upload_container:
            # File upload widget
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Select a PDF file containing CalTrans specifications",
                key="main_file_uploader"  # Add unique key to prevent conflicts
            )
            
            if uploaded_file is not None:
                st.info(f"File detected: {uploaded_file.name} ({uploaded_file.size} bytes)")
                
                # Process the file in a separate container to prevent layout issues
                process_container = st.container()
                with process_container:
                    return self._process_uploaded_file(uploaded_file)
        
        return None
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """Process the uploaded file with validation and progress tracking."""
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            # File validation
            validation_result = self._validate_file(uploaded_file)
            
            if not validation_result['valid']:
                self._display_error(validation_result['error'])
                return None
            
            # Display file info
            self._display_file_info(uploaded_file, validation_result)
            
            # Process file with progress
            processing_result = self._process_file_with_progress(uploaded_file)
            
            if processing_result['success']:
                self._display_success(uploaded_file.name)
                return processing_result['data']
            else:
                self._display_error(processing_result['error'])
                return None
    
    def _validate_file(self, uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file for size, type, and content."""
        
        # Check file size
        if uploaded_file.size > self.max_file_size:
            return {
                'valid': False,
                'error': f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (50MB)"
            }
        
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in self.allowed_extensions:
            return {
                'valid': False,
                'error': f"File type '{file_extension}' is not supported. Please upload a PDF file."
            }
        
        # Check if file is actually a PDF - improved validation
        try:
            # Read first few bytes to check PDF signature
            uploaded_file.seek(0)
            header = uploaded_file.read(8)  # Read more bytes for better detection
            uploaded_file.seek(0)  # Reset file pointer
            
            # Check for PDF signature (more flexible)
            if not header.startswith(b'%PDF'):
                # Try alternative PDF signatures
                if not (header.startswith(b'\x25\x50\x44\x46') or  # %PDF in hex
                       header.startswith(b'\x50\x4B\x03\x04')):   # ZIP format (some PDFs)
                    return {
                        'valid': False,
                        'error': "File does not appear to be a valid PDF document. Please ensure you're uploading a PDF file."
                    }
        except Exception as e:
            st.warning(f"Warning: Could not validate PDF signature: {str(e)}")
            # Continue anyway - let pdfplumber handle the actual validation
        
        return {
            'valid': True,
            'file_size': uploaded_file.size,
            'file_extension': file_extension
        }
    
    def _display_file_info(self, uploaded_file, validation_result: Dict[str, Any]):
        """Display file information in a clean format."""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "File Size",
                f"{validation_result['file_size'] / 1024 / 1024:.1f} MB"
            )
        
        with col2:
            st.metric(
                "File Type",
                validation_result['file_extension'].upper()
            )
        
        with col3:
            # Calculate file hash for identification
            uploaded_file.seek(0)
            file_hash = hashlib.md5(uploaded_file.read()).hexdigest()[:8]
            st.metric("File ID", file_hash)
        
        uploaded_file.seek(0)  # Reset file pointer
    
    def _process_file_with_progress(self, uploaded_file) -> Dict[str, Any]:
        """Process the PDF file with progress tracking."""
        
        # Set processing flag to prevent navigation issues
        st.session_state.is_processing_upload = True
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Reading PDF
            status_text.text("Reading PDF file...")
            progress_bar.progress(25)
            
            pdf_content = self._extract_pdf_content(uploaded_file)
            if not pdf_content:
                st.session_state.is_processing_upload = False
                return {
                    'success': False,
                    'error': "Failed to extract content from PDF file."
                }
            
            # Step 2: Analyzing content
            status_text.text("Analyzing document structure...")
            progress_bar.progress(50)
            
            analysis_result = self._analyze_pdf_content(pdf_content)
            
            # Step 3: Extracting text
            status_text.text("Extracting text content...")
            progress_bar.progress(75)
            
            text_content = self._extract_text_content(pdf_content)
            
            # Step 4: Finalizing
            status_text.text("Finalizing processing...")
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Get the raw PDF bytes for analysis
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            # Clear processing flag
            st.session_state.is_processing_upload = False
            
            return {
                'success': True,
                'data': {
                    'filename': uploaded_file.name,
                    'content': pdf_bytes,  # Pass raw PDF bytes instead of text
                    'text_content': text_content,  # Keep text content for other uses
                    'analysis': analysis_result,
                    'upload_time': datetime.now(),
                    'file_size': uploaded_file.size,
                    'pages': len(pdf_content) if pdf_content else 0
                }
            }
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            # Clear processing flag on error
            st.session_state.is_processing_upload = False
            return {
                'success': False,
                'error': f"Error processing file: {str(e)}"
            }
    
    def _extract_pdf_content(self, uploaded_file) -> Optional[list]:
        """Extract content from PDF file."""
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            with pdfplumber.open(uploaded_file) as pdf:
                pages = []
                for page in pdf.pages:
                    pages.append(page)
                return pages
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            st.info("This might be due to:")
            st.info("- File corruption")
            st.info("- Password protection")
            st.info("- Unsupported PDF format")
            st.info("- File is not actually a PDF")
            return None
    
    def _analyze_pdf_content(self, pdf_content: list) -> Dict[str, Any]:
        """Analyze PDF content structure."""
        analysis = {
            'total_pages': len(pdf_content),
            'has_tables': False,
            'has_images': False,
            'estimated_text_length': 0
        }
        
        for page in pdf_content:
            # Check for tables
            if page.extract_tables():
                analysis['has_tables'] = True
            
            # Check for images
            if page.images:
                analysis['has_images'] = True
            
            # Estimate text length
            text = page.extract_text() or ""
            analysis['estimated_text_length'] += len(text)
        
        return analysis
    
    def _extract_text_content(self, pdf_content: list) -> str:
        """Extract text content from PDF pages."""
        text_content = []
        
        for i, page in enumerate(pdf_content):
            text = page.extract_text()
            if text:
                text_content.append(f"--- Page {i+1} ---\n{text}\n")
        
        return "\n".join(text_content)
    
    def _display_error(self, error_message: str):
        """Display error message with styling."""
        st.error(f"❌ Upload Error: {error_message}")
        
        # Provide helpful suggestions
        with st.expander("💡 Troubleshooting Tips"):
            st.markdown("""
            **Common issues and solutions:**
            - **File too large**: Try compressing the PDF or splitting it into smaller files
            - **Invalid PDF**: Ensure the file is a valid PDF document, not a renamed file
            - **Corrupted file**: Try opening the PDF in a PDF reader first
            - **Password protected**: Remove password protection before uploading
            """)
    
    def _display_success(self, filename: str):
        """Display success message with file details."""
        st.success(f"✅ Successfully uploaded: **{filename}**")
        
        # Show next steps
        with st.expander("📋 Next Steps"):
            st.markdown("""
            **Your file has been uploaded successfully!**
            
            You can now:
            1. **Review the extracted content** in the analysis section
            2. **Configure bid settings** in the bid generator
            3. **Generate pricing** based on the specifications
            4. **Download results** as Excel files
            """)


def render_batch_upload() -> list:
    """
    Render batch file upload component.
    
    Returns:
        List of processed file data
    """
    st.subheader("📁 Batch Upload")
    st.markdown("Upload multiple PDF files at once for batch processing.")
    
    uploaded_files = st.file_uploader(
        "Choose multiple PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select multiple PDF files for batch processing"
    )
    
    if uploaded_files:
        uploader = FileUploadComponent()
        processed_files = []
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")
            
            result = uploader._process_uploaded_file(file)
            if result:
                processed_files.append(result)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        progress_bar.empty()
        status_text.empty()
        
        if processed_files:
            st.success(f"✅ Successfully processed {len(processed_files)} out of {len(uploaded_files)} files")
        
        return processed_files
    
    return []


def render_file_history() -> None:
    """Render file upload history and management."""
    st.subheader("📚 Upload History")
    
    # This would typically connect to a database or session state
    # For now, we'll show a placeholder
    if 'upload_history' not in st.session_state:
        st.session_state.upload_history = []
    
    if st.session_state.upload_history:
        for i, file_info in enumerate(st.session_state.upload_history):
            with st.expander(f"📄 {file_info.get('filename', 'Unknown file')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Uploaded:** {file_info.get('upload_time', 'Unknown')}")
                
                with col2:
                    st.write(f"**Size:** {file_info.get('file_size', 0) / 1024 / 1024:.1f} MB")
                
                with col3:
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.upload_history.pop(i)
                        # Remove the st.rerun() call to prevent jumping back to main screen
                        st.success("File removed from history")
    else:
        st.info("No files uploaded yet. Upload your first PDF to see it here.") 