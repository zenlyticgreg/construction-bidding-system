"""
Base model classes for PACE application.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configuration and methods."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        use_enum_values=True,
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model from dictionary."""
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """Create model from JSON string."""
        return cls.model_validate_json(json_str)


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class IdentifiableModel(BaseModel):
    """Base model with ID field."""
    
    id: Optional[str] = Field(default=None, description="Unique identifier")
    
    def generate_id(self) -> str:
        """Generate a unique ID if not already set."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        return self.id 