"""
Project-related data models for PACE application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from .base import TimestampedModel, IdentifiableModel, Field


class ProjectType(str, Enum):
    """Types of construction projects."""
    HIGHWAY = "highway"
    BRIDGE = "bridge"
    MUNICIPAL = "municipal"
    FEDERAL = "federal"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    RESIDENTIAL = "residential"


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SpecificationType(str, Enum):
    """Types of project specifications."""
    MATERIALS = "materials"
    EQUIPMENT = "equipment"
    LABOR = "labor"
    QUALITY = "quality"
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"


class ProjectSpecification(TimestampedModel, IdentifiableModel):
    """Model for project specifications."""
    
    project_id: str = Field(description="Associated project ID")
    type: SpecificationType = Field(description="Type of specification")
    section: str = Field(description="Specification section")
    title: str = Field(description="Specification title")
    content: str = Field(description="Specification content")
    requirements: List[str] = Field(default_factory=list, description="Specific requirements")
    standards: List[str] = Field(default_factory=list, description="Applicable standards")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    def add_requirement(self, requirement: str) -> None:
        """Add a requirement to the specification."""
        if requirement not in self.requirements:
            self.requirements.append(requirement)
            self.update_timestamp()
    
    def add_standard(self, standard: str) -> None:
        """Add a standard to the specification."""
        if standard not in self.standards:
            self.standards.append(standard)
            self.update_timestamp()


class QuantityItem(TimestampedModel):
    """Model for quantity items in a project."""
    
    item_code: str = Field(description="Item code/identifier")
    description: str = Field(description="Item description")
    unit: str = Field(description="Unit of measurement")
    quantity: float = Field(description="Required quantity")
    unit_price: Optional[float] = Field(default=None, description="Unit price")
    total_price: Optional[float] = Field(default=None, description="Total price")
    category: Optional[str] = Field(default=None, description="Item category")
    specifications: Optional[str] = Field(default=None, description="Item specifications")
    
    def calculate_total(self) -> float:
        """Calculate total price if unit price is available."""
        if self.unit_price is not None:
            self.total_price = self.quantity * self.unit_price
        return self.total_price or 0.0


class ProjectAnalysis(TimestampedModel, IdentifiableModel):
    """Model for project analysis results."""
    
    project_id: str = Field(description="Associated project ID")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    total_items: int = Field(description="Total number of items identified")
    total_quantity: float = Field(description="Total quantity across all items")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated total cost")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Analysis confidence score")
    items: List[QuantityItem] = Field(default_factory=list, description="Identified items")
    specifications: List[ProjectSpecification] = Field(default_factory=list, description="Extracted specifications")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")
    
    def add_item(self, item: QuantityItem) -> None:
        """Add an item to the analysis."""
        self.items.append(item)
        self.total_items = len(self.items)
        self.total_quantity += item.quantity
        self.update_timestamp()
    
    def calculate_estimated_cost(self) -> float:
        """Calculate total estimated cost from all items."""
        total = sum(item.calculate_total() for item in self.items)
        self.estimated_cost = total
        return total


class Project(TimestampedModel, IdentifiableModel):
    """Model for construction projects."""
    
    name: str = Field(description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    project_type: ProjectType = Field(description="Type of construction project")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Project status")
    
    # Agency information
    agency: str = Field(description="Agency or client name")
    agency_code: Optional[str] = Field(default=None, description="Agency project code")
    contract_number: Optional[str] = Field(default=None, description="Contract number")
    
    # Project details
    location: Optional[str] = Field(default=None, description="Project location")
    start_date: Optional[datetime] = Field(default=None, description="Project start date")
    end_date: Optional[datetime] = Field(default=None, description="Project end date")
    budget: Optional[float] = Field(default=None, description="Project budget")
    
    # File information
    specification_files: List[str] = Field(default_factory=list, description="Specification file paths")
    drawing_files: List[str] = Field(default_factory=list, description="Drawing file paths")
    
    # Analysis and bidding
    analysis: Optional[ProjectAnalysis] = Field(default=None, description="Project analysis results")
    bid_count: int = Field(default=0, description="Number of bids generated")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Project tags")
    notes: Optional[str] = Field(default=None, description="Project notes")
    
    def add_specification_file(self, file_path: str) -> None:
        """Add a specification file to the project."""
        if file_path not in self.specification_files:
            self.specification_files.append(file_path)
            self.update_timestamp()
    
    def add_drawing_file(self, file_path: str) -> None:
        """Add a drawing file to the project."""
        if file_path not in self.drawing_files:
            self.drawing_files.append(file_path)
            self.update_timestamp()
    
    def set_analysis(self, analysis: ProjectAnalysis) -> None:
        """Set the project analysis results."""
        self.analysis = analysis
        self.update_timestamp()
    
    def increment_bid_count(self) -> None:
        """Increment the bid count."""
        self.bid_count += 1
        self.update_timestamp()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    @property
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status in [ProjectStatus.IN_REVIEW, ProjectStatus.APPROVED, ProjectStatus.IN_PROGRESS]
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED 