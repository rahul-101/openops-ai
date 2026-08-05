"""
In-memory user repository implementation with default users.
"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from passlib.context import CryptContext

from app.infrastructure.auth.types import User


class InMemoryUserRepository:
    """
    In-memory user repository implementation with default users.
    """
    
    def __init__(self):
        self._users = {}
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize with default users for development."""
        default_users = [
            {
                "username": "admin",
                "email": "admin@openops.ai",
                "full_name": "Admin User",
                "role": "admin",
                "is_superuser": True,
                "is_active": True,
                "password": "fpSRu2dp8N9DFr"
            },
            {
                "username": "operator",
                "email": "operator@openops.ai",
                "full_name": "Operator User",
                "role": "operator",
                "is_superuser": False,
                "is_active": True,
                "password": "operator123"
            },
            {
                "username": "viewer",
                "email": "viewer@openops.ai",
                "full_name": "Viewer User",
                "role": "viewer",
                "is_superuser": False,
                "is_active": True,
                "password": "viewer123"
            },
            {
                "username": "user",
                "email": "user@openops.ai",
                "full_name": "Regular User",
                "role": "user",
                "is_superuser": False,
                "is_active": True,
                "password": "user123"
            }
        ]
        
        for user_data in default_users:
            password = user_data.pop("password")
            hashed_password = self._pwd_context.hash(password)
            user = User(
                id=str(uuid4()),
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                is_superuser=user_data["is_superuser"],
                is_active=user_data["is_active"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self._users[user.username] = user
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        self._users[user.username] = user
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self._users.get(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def update_user(self, user: User) -> User:
        """Update an existing user."""
        self._users[user.username] = user
        return user
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self._users:
            del self._users[username]
            return True
        return False
    
    def list_users(self) -> List[User]:
        """List all users."""
        return list(self._users.values())