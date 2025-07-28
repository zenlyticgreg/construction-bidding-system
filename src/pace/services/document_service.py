"""
Document service for managing file storage and document operations.
"""

import os
import shutil
import mimetypes
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json

from ..core.logging import get_module_logger
from ..core.config import settings
from ..models.document import Document, DocumentVersion, DocumentType, DocumentStatus
from ..models.user import User

logger = get_module_logger("services.document")


class DocumentService:
    """Service for managing documents and file storage."""
    
    def __init__(self):
        self.documents_file = settings.data_dir / "documents.json"
        self.documents_file.parent.mkdir(parents=True, exist_ok=True)
        self._documents: Dict[str, Document] = {}
        self._load_documents()
        
        # Create storage directories
        self.storage_root = settings.data_dir / "documents"
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different document types
        for doc_type in DocumentType:
            (self.storage_root / doc_type.value).mkdir(exist_ok=True)
    
    def _load_documents(self) -> None:
        """Load documents from storage."""
        try:
            if self.documents_file.exists():
                with open(self.documents_file, 'r') as f:
                    data = json.load(f)
                    for doc_data in data.values():
                        document = Document.model_validate(doc_data)
                        self._documents[document.id] = document
                logger.info(f"Loaded {len(self._documents)} documents from storage")
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
    
    def _save_documents(self) -> None:
        """Save documents to storage."""
        try:
            data = {doc.id: doc.model_dump() for doc in self._documents.values()}
            with open(self.documents_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved {len(self._documents)} documents to storage")
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
    
    def _get_storage_path(self, document_type: DocumentType, filename: str) -> Path:
        """Get storage path for a document."""
        # Create a unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        return self.storage_root / document_type.value / unique_filename
    
    def _save_file_content(self, file_path: Path, content: bytes) -> bool:
        """Save file content to disk."""
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    def create_document(
        self,
        project_id: str,
        name: str,
        document_type: DocumentType,
        original_filename: str,
        file_content: bytes,
        created_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> Tuple[Document, DocumentVersion]:
        """Create a new document with initial version."""
        
        # Create document
        document = Document(
            project_id=project_id,
            name=name,
            type=document_type,
            original_filename=original_filename,
            created_by=created_by,
            description=description,
            tags=tags or [],
            category=category,
        )
        document.generate_id()
        
        # Create initial version
        version = self._create_document_version(
            document=document,
            file_content=file_content,
            uploaded_by=created_by
        )
        
        # Add version to document
        document.add_version(version)
        
        # Save document
        self._documents[document.id] = document
        self._save_documents()
        
        logger.info(f"Created document: {document.name} (ID: {document.id})")
        return document, version
    
    def _create_document_version(
        self,
        document: Document,
        file_content: bytes,
        uploaded_by: str,
        upload_notes: Optional[str] = None
    ) -> DocumentVersion:
        """Create a new document version."""
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(document.original_filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Get storage path
        storage_path = self._get_storage_path(document.type, document.original_filename)
        
        # Save file content
        if not self._save_file_content(storage_path, file_content):
            raise Exception(f"Failed to save file content to {storage_path}")
        
        # Create version
        version = DocumentVersion(
            document_id=document.id,
            file_path=str(storage_path),
            file_size=len(file_content),
            file_hash=file_hash,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
            upload_notes=upload_notes,
        )
        version.generate_id()
        
        return version
    
    def add_document_version(
        self,
        document_id: str,
        file_content: bytes,
        uploaded_by: str,
        upload_notes: Optional[str] = None
    ) -> Optional[DocumentVersion]:
        """Add a new version to an existing document."""
        
        document = self.get_document(document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return None
        
        # Create new version
        version = self._create_document_version(
            document=document,
            file_content=file_content,
            uploaded_by=uploaded_by,
            upload_notes=upload_notes
        )
        
        # Add to document
        document.add_version(version)
        
        # Save changes
        self._save_documents()
        
        logger.info(f"Added version {version.version_number} to document {document.name}")
        return version
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self._documents.get(document_id)
    
    def get_documents_by_project(self, project_id: str) -> List[Document]:
        """Get all documents for a project."""
        return [doc for doc in self._documents.values() if doc.project_id == project_id]
    
    def get_documents_by_type(self, document_type: DocumentType) -> List[Document]:
        """Get documents by type."""
        return [doc for doc in self._documents.values() if doc.type == document_type]
    
    def get_documents_by_user(self, user_id: str) -> List[Document]:
        """Get documents created by a user."""
        return [doc for doc in self._documents.values() if doc.created_by == user_id]
    
    def get_document_version(self, document_id: str, version_id: str) -> Optional[DocumentVersion]:
        """Get a specific document version."""
        document = self.get_document(document_id)
        if not document:
            return None
        
        for version in document.versions:
            if version.id == version_id:
                return version
        
        return None
    
    def update_document_status(self, document_id: str, status: DocumentStatus) -> bool:
        """Update document status."""
        document = self.get_document(document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        document.status = status
        self._save_documents()
        
        logger.info(f"Updated document {document_id} status to {status}")
        return True
    
    def update_version_status(self, document_id: str, version_id: str, status: DocumentStatus) -> bool:
        """Update document version status."""
        version = self.get_document_version(document_id, version_id)
        if not version:
            logger.warning(f"Document version not found: {document_id}/{version_id}")
            return False
        
        version.processing_status = status
        self._save_documents()
        
        logger.info(f"Updated document version {version_id} status to {status}")
        return True
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its files."""
        document = self.get_document(document_id)
        if not document:
            logger.warning(f"Document not found for deletion: {document_id}")
            return False
        
        # Delete all version files
        for version in document.versions:
            try:
                file_path = Path(version.file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {version.file_path}: {e}")
        
        # Remove from storage
        del self._documents[document_id]
        self._save_documents()
        
        logger.info(f"Deleted document: {document.name} (ID: {document_id})")
        return True
    
    def get_file_content(self, document_id: str, version_id: Optional[str] = None) -> Optional[bytes]:
        """Get file content for a document version."""
        document = self.get_document(document_id)
        if not document:
            return None
        
        # Get version
        if version_id:
            version = self.get_document_version(document_id, version_id)
        else:
            version = document.get_current_version()
        
        if not version:
            return None
        
        # Read file content
        try:
            with open(version.file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {version.file_path}: {e}")
            return None
    
    def search_documents(
        self,
        query: str,
        project_id: Optional[str] = None,
        document_type: Optional[DocumentType] = None
    ) -> List[Document]:
        """Search documents by name, description, or tags."""
        query = query.lower()
        results = []
        
        for document in self._documents.values():
            # Filter by project if specified
            if project_id and document.project_id != project_id:
                continue
            
            # Filter by type if specified
            if document_type and document.type != document_type:
                continue
            
            # Search in name, description, and tags
            if (query in document.name.lower() or
                (document.description and query in document.description.lower()) or
                any(query in tag.lower() for tag in document.tags)):
                results.append(document)
        
        return results
    
    def get_document_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get document statistics."""
        documents = self._documents.values()
        
        if project_id:
            documents = [doc for doc in documents if doc.project_id == project_id]
        
        total_documents = len(documents)
        total_size = sum(doc.total_size for doc in documents)
        total_versions = sum(doc.version_count for doc in documents)
        
        # Count by type
        documents_by_type = {}
        for doc_type in DocumentType:
            documents_by_type[doc_type.value] = len(
                [doc for doc in documents if doc.type == doc_type]
            )
        
        # Count by status
        documents_by_status = {}
        for status in DocumentStatus:
            documents_by_status[status.value] = len(
                [doc for doc in documents if doc.status == status]
            )
        
        return {
            "total_documents": total_documents,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_versions": total_versions,
            "documents_by_type": documents_by_type,
            "documents_by_status": documents_by_status,
        } 