"""
MongoDB user repository implementation with default users.
"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from passlib.context import CryptContext

from app.infrastructure.auth.types import User
from pymongo import MongoClient
from app.core.config import settings


class MongoUserRepository:
    """
    MongoDB user repository implementation with default users.
    """
    
    def __init__(self):
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
        self._client = MongoClient(settings.MONGODB_URI)
        self._db = self._client[settings.DATABASE_NAME]
        self._collection = self._db["users"]
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize with default users if collection is empty."""
        if self._collection.count_documents({}) == 0:
            default_users = [
                {
                    "username": "admin",
                    "email": "admin@openops.ai",
                    "full_name": "Admin User",
                    "role": "admin",
                    "is_superuser": True,
                    "is_active": True,
                    "password": "admin123"
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
                user_dict = user.dict()
                self._collection.insert_one(user_dict)
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        user_dict = user.dict()
        result = self._collection.insert_one(user_dict)
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_dict = self._collection.find_one({"username": username})
        if user_dict:
            return User(**user_dict)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_dict = self._collection.find_one({"email": email})
        if user_dict:
            return User(**user_dict)
        return None
    
    def update_user(self, user: User) -> User:
        """Update an existing user."""
        user_dict = user.dict()
        result = self._collection.update_one(
            {"username": user.username},
            {"$set": user_dict}
        )
        
        if result.modified_count > 0:
            return user
        return None
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        result = self._collection.delete_one({"username": username})
        return result.deleted_count > 0
    
    def list_users(self) -> List[User]:
        """List all users."""
        users = []
        for user_dict in self._collection.find():
            users.append(User(**user_dict))
        return users