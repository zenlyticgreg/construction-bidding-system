"""
Document management models for PACE application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
import hashlib
import mimetypes
from .base import TimestampedModel, IdentifiableModel, Field


class DocumentType(str, Enum):
    """Document type enumeration."""
    SPECIFICATION = "specification"
    DRAWING = "drawing"
    BID_FORM = "bid_form"
    CONTRACT = "contract"
    PERMIT = "permit"
    INSPECTION = "inspection"
    PHOTO = "photo"
    REPORT = "report"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status enumeration."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    ERROR = "error"


class DocumentVersion(TimestampedModel, IdentifiableModel):
    """Model for document versions."""
    
    document_id: str = Field(description="Parent document ID")
    version_number: int = Field(description="Version number")
    file_path: str = Field(description="File storage path")
    file_size: int = Field(description="File size in bytes")
    file_hash: str = Field(description="File content hash")
    mime_type: str = Field(description="File MIME type")
    
    # Processing metadata
    processing_status: DocumentStatus = Field(default=DocumentStatus.UPLOADING, description="Processing status")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors")
    extracted_text: Optional[str] = Field(default=None, description="Extracted text content")
    page_count: Optional[int] = Field(default=None, description="Number of pages")
    
    # Analysis results
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Analysis confidence")
    
    # Metadata
    uploaded_by: str = Field(description="User ID who uploaded this version")
    upload_notes: Optional[str] = Field(default=None, description="Upload notes")
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()
    
    def get_file_extension(self) -> str:
        """Get file extension from MIME type."""
        return mimetypes.guess_extension(self.mime_type) or ""
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF."""
        return self.mime_type == "application/pdf"
    
    def is_image(self) -> bool:
        """Check if document is an image."""
        return self.mime_type.startswith("image/")


class Document(TimestampedModel, IdentifiableModel):
    """Model for documents in the system."""
    
    project_id: str = Field(description="Associated project ID")
    name: str = Field(description="Document name")
    type: DocumentType = Field(description="Document type")
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADING, description="Document status")
    
    # File information
    original_filename: str = Field(description="Original uploaded filename")
    current_version: Optional[str] = Field(default=None, description="Current version ID")
    versions: List[DocumentVersion] = Field(default_factory=list, description="Document versions")
    
    # Metadata
    description: Optional[str] = Field(default=None, description="Document description")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    category: Optional[str] = Field(default=None, description="Document category")
    
    # Access control
    created_by: str = Field(description="User ID who created the document")
    accessible_by: List[str] = Field(default_factory=list, description="Users who can access this document")
    
    # Project-specific metadata
    agency_code: Optional[str] = Field(default=None, description="Agency project code")
    contract_number: Optional[str] = Field(default=None, description="Contract number")
    section_number: Optional[str] = Field(default=None, description="Specification section number")
    
    def add_version(self, version: DocumentVersion) -> None:
        """Add a new version to the document."""
        # Set version number
        version.version_number = len(self.versions) + 1
        
        # Add to versions list
        self.versions.append(version)
        
        # Set as current version
        self.current_version = version.id
        
        # Update status
        self.status = version.processing_status
        
        self.update_timestamp()
    
    def get_current_version(self) -> Optional[DocumentVersion]:
        """Get the current version of the document."""
        if not self.current_version:
            return None
        
        for version in self.versions:
            if version.id == self.current_version:
                return version
        
        return None
    
    def get_latest_version(self) -> Optional[DocumentVersion]:
        """Get the latest version of the document."""
        if not self.versions:
            return None
        
        return max(self.versions, key=lambda v: v.version_number)
    
    def get_version_by_number(self, version_number: int) -> Optional[DocumentVersion]:
        """Get a specific version by number."""
        for version in self.versions:
            if version.version_number == version_number:
                return version
        
        return None
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()
    
    def grant_access(self, user_id: str) -> None:
        """Grant access to a user."""
        if user_id not in self.accessible_by:
            self.accessible_by.append(user_id)
            self.update_timestamp()
    
    def revoke_access(self, user_id: str) -> None:
        """Revoke access from a user."""
        if user_id in self.accessible_by:
            self.accessible_by.remove(user_id)
            self.update_timestamp()
    
    def can_user_access(self, user_id: str) -> bool:
        """Check if a user can access this document."""
        return user_id in self.accessible_by or user_id == self.created_by
    
    @property
    def total_size(self) -> int:
        """Get total size of all versions."""
        return sum(version.file_size for version in self.versions)
    
    @property
    def version_count(self) -> int:
        """Get number of versions."""
        return len(self.versions) 