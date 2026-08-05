"""
User repository initialization for OpenOps AI.
"""

from app.core.config import get_settings
from app.infrastructure.persistence.user_repository import get_user_repository
from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
from app.infrastructure.auth.types import User as DomainUser


async def setup_user_repository():
    """
    Initialize the user repository with default users if needed.
    """
    user_repo = get_user_repository()
    
    if hasattr(user_repo, '_users') and len(user_repo._users) == 0:
        settings = get_settings()
        
        # Create default admin user if no users exist
        admin_user = DomainUser(
            username=settings.ADMIN_USERNAME or "admin",
            email=settings.ADMIN_EMAIL or "admin@openops.ai",
            full_name=settings.ADMIN_FULL_NAME or "Admin User",
            hashed_password=settings.ADMIN_PASSWORD_HASH or "$2b$12$EroCAXWMqZelJ6Crtn0.PuGLRT9gWaveHb4CUuFW7pCwYggdCLnFS",  # password: admin123
            is_active=True,
            is_superuser=True,
            role="admin",
        )
        user_repo.create_user(admin_user)
        
        # Create default operator user
        operator_user = DomainUser(
            username="operator",
            email="operator@openops.ai",
            full_name="Operator User",
            hashed_password="$2b$12$EroCAXWMqZelJ6Crtn0.PuGLRT9gWaveHb4CUuFW7pCwYggdCLnFS",  # password: admin123
            is_active=True,
            is_superuser=False,
            role="operator",
        )
        user_repo.create_user(operator_user)
        
        print("Initialized user repository with default users")
    
    return user_repo


def get_user_repository_instance():
    """Get the user repository instance."""
    return get_user_repository()