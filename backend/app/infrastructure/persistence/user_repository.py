"""
User repository implementation that handles both InMemory and MongoDB.
"""

from typing import List, Optional
from app.infrastructure.auth.types import User
from app.core.config import get_settings


def get_user_repository():
    """Get the appropriate user repository based on configuration."""
    settings = get_settings()
    if settings.REPOSITORY_TYPE == "mongo":
        from app.infrastructure.persistence.mongo.mongo_user_repository import MongoUserRepository
        return MongoUserRepository()
    else:
        from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
        return InMemoryUserRepository()


def get_user_repository_instance():
    """Get the user repository instance."""
    return get_user_repository()