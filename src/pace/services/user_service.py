"""
User service for managing users and authentication.
"""

import json
import hashlib
import secrets
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..core.logging import get_module_logger
from ..core.config import settings
from ..models.user import User, UserRole, UserStatus

logger = get_module_logger("services.user")


class UserService:
    """Service for managing users and authentication."""
    
    def __init__(self):
        self.users_file = settings.data_dir / "users.json"
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, User] = {}
        self._load_users()
        
        # Create default admin user if no users exist
        if not self._users:
            self._create_default_admin()
    
    def _load_users(self) -> None:
        """Load users from storage."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data.values():
                        user = User.model_validate(user_data)
                        self._users[user.id] = user
                logger.info(f"Loaded {len(self._users)} users from storage")
        except Exception as e:
            logger.error(f"Error loading users: {e}")
    
    def _save_users(self) -> None:
        """Save users to storage."""
        try:
            data = {user.id: user.model_dump() for user in self._users.values()}
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved {len(self._users)} users to storage")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _create_default_admin(self) -> None:
        """Create a default admin user."""
        admin_user = User(
            username="admin",
            email="admin@pace-construction.com",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            company="PACE Construction",
            department="IT",
            position="System Administrator",
        )
        admin_user.generate_id()
        
        # Set a default password (should be changed on first login)
        admin_user.password_hash = self._hash_password("admin123")
        
        self._users[admin_user.id] = admin_user
        self._save_users()
        
        logger.info("Created default admin user")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return self._hash_password(password) == password_hash
    
    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: UserRole = UserRole.ESTIMATOR,
        company: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
    ) -> Optional[User]:
        """Create a new user."""
        
        # Check if username already exists
        if self.get_user_by_username(username):
            logger.warning(f"Username already exists: {username}")
            return None
        
        # Check if email already exists
        if self.get_user_by_email(email):
            logger.warning(f"Email already exists: {email}")
            return None
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            company=company,
            department=department,
            position=position,
        )
        user.generate_id()
        user.password_hash = self._hash_password(password)
        
        # Save user
        self._users[user.id] = user
        self._save_users()
        
        logger.info(f"Created user: {user.username} (ID: {user.id})")
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.get_user_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: username not found: {username}")
            return None
        
        # Check if account is locked
        if user.is_locked():
            logger.warning(f"Authentication failed: account locked for user: {username}")
            return None
        
        # Check if account is active
        if not user.is_active():
            logger.warning(f"Authentication failed: account not active for user: {username}")
            return None
        
        # Verify password
        if not user.password_hash or not self._verify_password(password, user.password_hash):
            user.increment_failed_login()
            self._save_users()
            logger.warning(f"Authentication failed: invalid password for user: {username}")
            return None
        
        # Authentication successful
        user.update_last_login()
        self._save_users()
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self._users.values())
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role."""
        return [user for user in self._users.values() if user.role == role]
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return [user for user in self._users.values() if user.is_active()]
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update a user."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
        
        # Handle password update separately
        if 'password' in kwargs:
            password = kwargs.pop('password')
            user.password_hash = self._hash_password(password)
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.update_timestamp()
        self._save_users()
        
        logger.info(f"Updated user: {user.username} (ID: {user_id})")
        return user
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change a user's password."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return False
        
        # Verify current password
        if not user.password_hash or not self._verify_password(current_password, user.password_hash):
            logger.warning(f"Password change failed: invalid current password for user: {user.username}")
            return False
        
        # Update password
        user.password_hash = self._hash_password(new_password)
        user.update_timestamp()
        self._save_users()
        
        logger.info(f"Password changed for user: {user.username}")
        return True
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset a user's password (admin function)."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return False
        
        # Update password
        user.password_hash = self._hash_password(new_password)
        user.reset_failed_login()  # Also unlock account if locked
        user.update_timestamp()
        self._save_users()
        
        logger.info(f"Password reset for user: {user.username}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found for deletion: {user_id}")
            return False
        
        # Don't allow deletion of the last admin user
        if user.role == UserRole.ADMIN:
            admin_users = self.get_users_by_role(UserRole.ADMIN)
            if len(admin_users) <= 1:
                logger.warning("Cannot delete the last admin user")
                return False
        
        del self._users[user_id]
        self._save_users()
        
        logger.info(f"Deleted user: {user.username} (ID: {user_id})")
        return True
    
    def lock_user(self, user_id: str) -> bool:
        """Lock a user account."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return False
        
        user.status = UserStatus.SUSPENDED
        user.update_timestamp()
        self._save_users()
        
        logger.info(f"Locked user: {user.username}")
        return True
    
    def unlock_user(self, user_id: str) -> bool:
        """Unlock a user account."""
        user = self.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            return False
        
        user.status = UserStatus.ACTIVE
        user.reset_failed_login()
        user.update_timestamp()
        self._save_users()
        
        logger.info(f"Unlocked user: {user.username}")
        return True
    
    def search_users(self, query: str) -> List[User]:
        """Search users by username, email, or full name."""
        query = query.lower()
        results = []
        
        for user in self._users.values():
            if (query in user.username.lower() or
                query in user.email.lower() or
                query in user.full_name.lower()):
                results.append(user)
        
        return results
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = len(self._users)
        active_users = len(self.get_active_users())
        locked_users = len([u for u in self._users.values() if u.is_locked()])
        
        # Count by role
        users_by_role = {}
        for role in UserRole:
            users_by_role[role.value] = len(self.get_users_by_role(role))
        
        # Count by status
        users_by_status = {}
        for status in UserStatus:
            users_by_status[status.value] = len(
                [u for u in self._users.values() if u.status == status]
            )
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "users_by_role": users_by_role,
            "users_by_status": users_by_status,
        } 