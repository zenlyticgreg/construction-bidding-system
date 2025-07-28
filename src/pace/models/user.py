"""
User management models for PACE application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from .base import TimestampedModel, IdentifiableModel, Field


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    ESTIMATOR = "estimator"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(TimestampedModel, IdentifiableModel):
    """Model for application users."""
    
    username: str = Field(description="Unique username")
    email: str = Field(description="User email address")
    full_name: str = Field(description="User's full name")
    role: UserRole = Field(default=UserRole.ESTIMATOR, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    
    # Company/Organization information
    company: Optional[str] = Field(default=None, description="Company name")
    department: Optional[str] = Field(default=None, description="Department")
    position: Optional[str] = Field(default=None, description="Job position")
    
    # Contact information
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Address")
    
    # Preferences
    default_agency: Optional[str] = Field(default="caltrans", description="Default agency")
    timezone: str = Field(default="UTC", description="User timezone")
    language: str = Field(default="en", description="Preferred language")
    
    # Security
    password_hash: Optional[str] = Field(default=None, description="Hashed password")
    last_login: Optional[datetime] = Field(default=None, description="Last login time")
    failed_login_attempts: int = Field(default=0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(default=None, description="Account locked until")
    
    # Metadata
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    notes: Optional[str] = Field(default=None, description="User notes")
    
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def can_access_project(self, project_id: str) -> bool:
        """Check if user can access a specific project."""
        # Admin can access all projects
        if self.role == UserRole.ADMIN:
            return True
        
        # For now, all active users can access all projects
        # This can be enhanced with project-specific permissions later
        return self.is_active() and not self.is_locked()
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        self.update_timestamp()
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + datetime.timedelta(minutes=30)
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.update_timestamp()
    
    def update_last_login(self) -> None:
        """Update last login time."""
        self.last_login = datetime.utcnow()
        self.reset_failed_login()
        self.update_timestamp() 