"""Authentication types and schemas."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import uuid4


class User(BaseModel):
    """Domain model representing an authenticated user."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password."""
        from passlib.context import CryptContext
        crypt_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
        return crypt_context.verify(self.hashed_password, password)

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return self.role == role or self.is_superuser

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if self.is_superuser:
            return True
        return self.role in self.get_permissions_for_role(self.role)

    def get_permissions_for_role(self, role: str) -> list[str]:
        """Get permissions for a role."""
        if role == "user":
            return ["read", "write"]
        elif role == "admin":
            return ["read", "write", "admin"]
        return []


class TokenData(BaseModel):
    """Data embedded in JWT token."""
    username: str
    user_id: Optional[str] = None


class LoginForm(BaseModel):
    """Login form schema."""
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")


class RegisterForm(BaseModel):
    """Registration form schema."""
    name: str = Field(min_length=2, description="Name must be at least 2 characters")
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    confirm_password: str

    def __init__(self, **data):
        super().__init__(**data)
        if hasattr(self, 'password') and hasattr(self, 'confirm_password'):
            if self.password != self.confirm_password:
                raise ValueError("Passwords don't match")


class ForgotPasswordForm(BaseModel):
    """Forgot password form schema."""
    email: EmailStr


class UserResponse(BaseModel):
    """User response model."""
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    role: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """Convert domain User to response model."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )