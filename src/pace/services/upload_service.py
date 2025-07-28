"""
Upload service for handling file uploads and processing.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import hashlib

from ..core.logging import get_module_logger
from ..core.config import settings
from ..models.document import DocumentType, DocumentStatus
from ..models.user import User
from .project_service import ProjectService
from .document_service import DocumentService
from .user_service import UserService

logger = get_module_logger("services.upload")


class UploadService:
    """Service for handling file uploads and processing."""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.document_service = DocumentService()
        self.user_service = UserService()
        
        # File validation settings
        self.max_file_size = settings.file.max_file_size
        self.allowed_extensions = settings.file.allowed_extensions
        
        # MIME type mapping
        self.mime_type_mapping = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
    
    def validate_file(
        self,
        filename: str,
        file_content: bytes,
        user_id: str
    ) -> Dict[str, Any]:
        """Validate an uploaded file."""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'file_info': {}
        }
        
        # Check file size
        file_size = len(file_content)
        if file_size > self.max_file_size:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size "
                f"({self.max_file_size / (1024*1024):.1f}MB)"
            )
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"File extension '{file_ext}' is not allowed. "
                f"Allowed extensions: {', '.join(self.allowed_extensions)}"
            )
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = self.mime_type_mapping.get(file_ext, 'application/octet-stream')
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicate files
        duplicate_check = self._check_duplicate_file(file_hash, user_id)
        if duplicate_check['is_duplicate']:
            validation_result['warnings'].append(
                f"Similar file already exists: {duplicate_check['existing_file']}"
            )
        
        # File information
        validation_result['file_info'] = {
            'filename': filename,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'file_extension': file_ext,
            'mime_type': mime_type,
            'file_hash': file_hash,
            'upload_timestamp': datetime.utcnow().isoformat(),
        }
        
        return validation_result
    
    def _check_duplicate_file(self, file_hash: str, user_id: str) -> Dict[str, Any]:
        """Check if a file with the same hash already exists."""
        user_documents = self.document_service.get_documents_by_user(user_id)
        
        for document in user_documents:
            current_version = document.get_current_version()
            if current_version and current_version.file_hash == file_hash:
                return {
                    'is_duplicate': True,
                    'existing_file': document.name,
                    'document_id': document.id
                }
        
        return {'is_duplicate': False}
    
    def determine_document_type(self, filename: str, mime_type: str) -> DocumentType:
        """Determine document type based on filename and MIME type."""
        filename_lower = filename.lower()
        
        # Check for specification files
        if any(keyword in filename_lower for keyword in ['spec', 'specification', 'specs']):
            return DocumentType.SPECIFICATION
        
        # Check for bid forms
        if any(keyword in filename_lower for keyword in ['bid', 'form', 'proposal', 'quote']):
            return DocumentType.BID_FORM
        
        # Check for drawings/plans
        if any(keyword in filename_lower for keyword in ['plan', 'drawing', 'blueprint', 'dwg', 'cad']):
            return DocumentType.DRAWING
        
        # Check for contracts
        if any(keyword in filename_lower for keyword in ['contract', 'agreement', 'terms']):
            return DocumentType.CONTRACT
        
        # Check for permits
        if any(keyword in filename_lower for keyword in ['permit', 'license', 'approval']):
            return DocumentType.PERMIT
        
        # Check for reports
        if any(keyword in filename_lower for keyword in ['report', 'analysis', 'summary']):
            return DocumentType.REPORT
        
        # Default based on MIME type
        if mime_type == 'application/pdf':
            return DocumentType.SPECIFICATION  # Default for PDFs
        elif mime_type.startswith('image/'):
            return DocumentType.DRAWING
        else:
            return DocumentType.OTHER
    
    def upload_file_to_project(
        self,
        project_id: str,
        filename: str,
        file_content: bytes,
        uploaded_by: str,
        document_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a file to a project."""
        
        result = {
            'success': False,
            'document': None,
            'project': None,
            'validation': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate file
            validation = self.validate_file(filename, file_content, uploaded_by)
            result['validation'] = validation
            
            if not validation['valid']:
                result['errors'] = validation['errors']
                return result
            
            result['warnings'] = validation['warnings']
            
            # Determine document type
            document_type = self.determine_document_type(
                filename, 
                validation['file_info']['mime_type']
            )
            
            # Use provided name or generate from filename
            if not document_name:
                document_name = Path(filename).stem
            
            # Add document to project
            upload_result = self.project_service.add_document_to_project(
                project_id=project_id,
                name=document_name,
                document_type=document_type,
                original_filename=filename,
                file_content=file_content,
                uploaded_by=uploaded_by,
                description=description,
                tags=tags,
                category=category,
            )
            
            if upload_result:
                project, document = upload_result
                result['success'] = True
                result['document'] = document
                result['project'] = project
                
                logger.info(f"Successfully uploaded {filename} to project {project.name}")
            else:
                result['errors'].append("Failed to add document to project")
                
        except Exception as e:
            result['errors'].append(f"Upload failed: {str(e)}")
            logger.error(f"Error uploading file {filename}: {e}")
        
        return result
    
    def upload_multiple_files(
        self,
        project_id: str,
        files: List[Tuple[str, bytes]],
        uploaded_by: str,
        file_metadata: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Upload multiple files to a project."""
        
        result = {
            'success': True,
            'uploaded_files': [],
            'failed_files': [],
            'total_files': len(files),
            'successful_uploads': 0,
            'failed_uploads': 0,
            'errors': [],
            'warnings': []
        }
        
        for i, (filename, file_content) in enumerate(files):
            # Get metadata for this file if available
            metadata = file_metadata[i] if file_metadata and i < len(file_metadata) else {}
            
            upload_result = self.upload_file_to_project(
                project_id=project_id,
                filename=filename,
                file_content=file_content,
                uploaded_by=uploaded_by,
                document_name=metadata.get('name'),
                description=metadata.get('description'),
                tags=metadata.get('tags'),
                category=metadata.get('category'),
            )
            
            if upload_result['success']:
                result['uploaded_files'].append({
                    'filename': filename,
                    'document': upload_result['document'],
                    'validation': upload_result['validation']
                })
                result['successful_uploads'] += 1
            else:
                result['failed_files'].append({
                    'filename': filename,
                    'errors': upload_result['errors']
                })
                result['failed_uploads'] += 1
                result['success'] = False
            
            # Collect warnings
            result['warnings'].extend(upload_result.get('warnings', []))
        
        logger.info(f"Multiple file upload completed: {result['successful_uploads']} successful, "
                   f"{result['failed_uploads']} failed")
        
        return result
    
    def get_upload_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get upload statistics."""
        if user_id:
            user_documents = self.document_service.get_documents_by_user(user_id)
            user_projects = self.project_service.get_projects_by_user(user_id)
        else:
            user_documents = self.document_service.get_all_documents()
            user_projects = self.project_service.get_all_projects()
        
        total_documents = len(user_documents)
        total_size = sum(doc.total_size for doc in user_documents)
        
        # Count by document type
        documents_by_type = {}
        for doc_type in DocumentType:
            documents_by_type[doc_type.value] = len(
                [doc for doc in user_documents if doc.type == doc_type]
            )
        
        # Count by status
        documents_by_status = {}
        for status in DocumentStatus:
            documents_by_status[status.value] = len(
                [doc for doc in user_documents if doc.status == status]
            )
        
        return {
            'total_documents': total_documents,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_projects': len(user_projects),
            'documents_by_type': documents_by_type,
            'documents_by_status': documents_by_status,
        } 