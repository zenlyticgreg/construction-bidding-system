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

logger = get_module_logger("services.project")


class ProjectService:
    """Service for managing construction projects."""
    
    def __init__(self):
        self.projects_file = settings.data_dir / "projects.json"
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        self._projects: Dict[str, Project] = {}
        self._load_projects()
    
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
        description: Optional[str] = None,
        location: Optional[str] = None,
        budget: Optional[float] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            project_type=project_type,
            agency=agency,
            description=description,
            location=location,
            budget=budget,
        )
        project.generate_id()
        
        self._projects[project.id] = project
        self._save_projects()
        
        logger.info(f"Created project: {project.name} (ID: {project.id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self._projects.get(project_id)
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        return list(self._projects.values())
    
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
        """Delete a project."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found for deletion: {project_id}")
            return False
        
        del self._projects[project_id]
        self._save_projects()
        
        logger.info(f"Deleted project: {project.name} (ID: {project_id})")
        return True
    
    def add_specification_file(self, project_id: str, file_path: str) -> bool:
        """Add a specification file to a project."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return False
        
        project.add_specification_file(file_path)
        self._save_projects()
        
        logger.info(f"Added specification file to project {project_id}: {file_path}")
        return True
    
    def add_drawing_file(self, project_id: str, file_path: str) -> bool:
        """Add a drawing file to a project."""
        project = self.get_project(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return False
        
        project.add_drawing_file(file_path)
        self._save_projects()
        
        logger.info(f"Added drawing file to project {project_id}: {file_path}")
        return True
    
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
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Get project statistics."""
        total_projects = len(self._projects)
        active_projects = len([p for p in self._projects.values() if p.is_active])
        completed_projects = len([p for p in self._projects.values() if p.is_completed])
        
        projects_by_type = {}
        for project_type in ProjectType:
            projects_by_type[project_type.value] = len(
                [p for p in self._projects.values() if p.project_type == project_type]
            )
        
        projects_by_status = {}
        for status in ProjectStatus:
            projects_by_status[status.value] = len(
                [p for p in self._projects.values() if p.status == status]
            )
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "projects_by_type": projects_by_type,
            "projects_by_status": projects_by_status,
        } 