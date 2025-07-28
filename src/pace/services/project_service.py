"""
Project service for managing construction projects.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.logging import get_module_logger
from ..core.config import settings
from ..models.project import Project, ProjectAnalysis, ProjectStatus, ProjectType
from ..models.document import DocumentType
from .document_service import DocumentService
from .user_service import UserService

logger = get_module_logger("services.project")


class ProjectService:
    """Service for managing construction projects."""
    
    def __init__(self):
        self.projects_file = settings.data_dir / "projects.json"
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        self._projects: Dict[str, Project] = {}
        self._load_projects()
        
        # Initialize related services
        self.document_service = DocumentService()
        self.user_service = UserService()
    
    def _load_projects(self) -> None:
        """Load projects from storage."""
        try:
            if self.projects_file.exists():
                with open(self.projects_file, 'r') as f:
                    data = json.load(f)
                    for project_data in data.values():
                        project = Project.model_validate(project_data)
                        self._projects[project.id] = project
                logger.info(f"Loaded {len(self._projects)} projects from storage")
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
    
    def _save_projects(self) -> None:
        """Save projects to storage."""
        try:
            data = {project.id: project.model_dump() for project in self._projects.values()}
            with open(self.projects_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved {len(self._projects)} projects to storage")
        except Exception as e:
            logger.error(f"Error saving projects: {e}")
    
    def create_project(
        self,
        name: str,
        project_type: ProjectType,
        agency: str,
        created_by: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        budget: Optional[float] = None,
        agency_code: Optional[str] = None,
        contract_number: Optional[str] = None,
    ) -> Project:
        """Create a new project."""
        
        # Verify user exists
        user = self.user_service.get_user(created_by)
        if not user:
            raise ValueError(f"User not found: {created_by}")
        
        project = Project(
            name=name,
            project_type=project_type,
            agency=agency,
            description=description,
            location=location,
            budget=budget,
        )
        project.generate_id()
        
        # Add project-specific metadata
        if agency_code:
            project.agency_code = agency_code
        if contract_number:
            project.contract_number = contract_number
        
        self._projects[project.id] = project
        self._save_projects()
        
        logger.info(f"Created project: {project.name} (ID: {project.id}) by user: {user.username}")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self._projects.get(project_id)
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        return list(self._projects.values())
    
    def get_projects_by_user(self, user_id: str) -> List[Project]:
        """Get projects accessible by a user."""
        user = self.user_service.get_user(user_id)
        if not user:
            return []
        
        # Admin can see all projects
        if user.role.value == "admin":
            return self.get_all_projects()
        
        # For now, all users can see all projects
        # This can be enhanced with project-specific permissions later
        return self.get_all_projects()
    
    def get_projects_by_status(self, status: ProjectStatus) -> List[Project]:
        """Get projects by status."""
        return [p for p in self._projects.values() if p.status == status]
    
    def get_projects_by_type(self, project_type: ProjectType) -> List[Project]:
        """Get projects by type."""
        return [p for p in self._projects.values() if p.project_type == project_type]
    
    def get_projects_by_agency(self, agency: str) -> List[Project]:
        """Get projects by agency."""
        return [p for p in self._projects.values() if p.agency.lower() == agency.lower()]
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.update_timestamp()
        self._save_projects()
        
        logger.info(f"Updated project: {project.name} (ID: {project_id})")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its documents."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found for deletion: {project_id}")
            return False
        
        # Delete all project documents
        project_documents = self.document_service.get_documents_by_project(project_id)
        for document in project_documents:
            self.document_service.delete_document(document.id)
        
        # Delete project
        del self._projects[project_id]
        self._save_projects()
        
        logger.info(f"Deleted project: {project.name} (ID: {project_id})")
        return True
    
    def add_document_to_project(
        self,
        project_id: str,
        name: str,
        document_type: DocumentType,
        original_filename: str,
        file_content: bytes,
        uploaded_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> Optional[tuple[Project, Document]]:
        """Add a document to a project."""
        
        # Verify project exists
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return None
        
        # Verify user exists
        user = self.user_service.get_user(uploaded_by)
        if not user:
            logger.warning(f"User not found: {uploaded_by}")
            return None
        
        try:
            # Create document
            document, version = self.document_service.create_document(
                project_id=project_id,
                name=name,
                document_type=document_type,
                original_filename=original_filename,
                file_content=file_content,
                created_by=uploaded_by,
                description=description,
                tags=tags,
                category=category,
            )
            
            # Update project file lists (for backward compatibility)
            if document_type == DocumentType.SPECIFICATION:
                project.add_specification_file(document.id)
            elif document_type == DocumentType.DRAWING:
                project.add_drawing_file(document.id)
            
            self._save_projects()
            
            logger.info(f"Added document {document.name} to project {project.name}")
            return project, document
            
        except Exception as e:
            logger.error(f"Error adding document to project: {e}")
            return None
    
    def get_project_documents(self, project_id: str) -> List[Document]:
        """Get all documents for a project."""
        return self.document_service.get_documents_by_project(project_id)
    
    def get_project_documents_by_type(self, project_id: str, document_type: DocumentType) -> List[Document]:
        """Get project documents by type."""
        documents = self.document_service.get_documents_by_project(project_id)
        return [doc for doc in documents if doc.type == document_type]
    
    def set_project_analysis(self, project_id: str, analysis: ProjectAnalysis) -> bool:
        """Set analysis results for a project."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return False
        
        project.set_analysis(analysis)
        self._save_projects()
        
        logger.info(f"Set analysis for project {project_id}")
        return True
    
    def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """Update project status."""
        return self.update_project(project_id, status=status) is not None
    
    def search_projects(self, query: str) -> List[Project]:
        """Search projects by name, description, or agency."""
        query = query.lower()
        results = []
        
        for project in self._projects.values():
            if (query in project.name.lower() or
                (project.description and query in project.description.lower()) or
                query in project.agency.lower()):
                results.append(project)
        
        return results
    
    def get_project_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get project statistics."""
        projects = self._projects.values()
        
        # Filter by user if specified
        if user_id:
            projects = self.get_projects_by_user(user_id)
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.is_active])
        completed_projects = len([p for p in projects if p.is_completed])
        
        projects_by_type = {}
        for project_type in ProjectType:
            projects_by_type[project_type.value] = len(
                [p for p in projects if p.project_type == project_type]
            )
        
        projects_by_status = {}
        for status in ProjectStatus:
            projects_by_status[status.value] = len(
                [p for p in projects if p.status == status]
            )
        
        # Document statistics
        total_documents = 0
        total_document_size = 0
        
        for project in projects:
            project_docs = self.document_service.get_documents_by_project(project.id)
            total_documents += len(project_docs)
            total_document_size += sum(doc.total_size for doc in project_docs)
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "projects_by_type": projects_by_type,
            "projects_by_status": projects_by_status,
            "total_documents": total_documents,
            "total_document_size_mb": round(total_document_size / (1024 * 1024), 2),
        } 