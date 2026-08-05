from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

from app.api.models.api_response import ApiResponse
from app.infrastructure.auth.types import User as DomainUser, ForgotPasswordForm, UserResponse
from app.core.config import get_settings
from app.infrastructure.persistence.user_repository import get_user_repository

router = APIRouter()

# JWT settings
settings = get_settings()

if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in settings")

if not settings.ALGORITHM:
    raise RuntimeError("ALGORITHM is not set in settings")

class LoginForm(BaseModel):
    """Login form schema."""
    username: str
    password: str

class RegisterForm(BaseModel):
    """Register form schema."""
    name: str
    email: str
    password: str
    confirm_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

# Dependency to get current user
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = get_user_repository()
    user = user_repo.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/login", response_model=ApiResponse, tags=["Auth"])
async def login(form_data: LoginForm):
    """Authenticate user and return access token."""
    user_repo = get_user_repository()
    user = user_repo.get_user_by_email(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role, "is_superuser": user.is_superuser},
        expires_delta=access_token_expires
    )
    
    return ApiResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_domain(user)
        },
    )

@router.post("/register", response_model=ApiResponse, tags=["Auth"])
async def register(form_data: RegisterForm):
    """Register a new user."""
    if form_data.password != form_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords don't match"
        )
    
    if len(form_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    user_repo = get_user_repository()
    
    # Check if user already exists
    if user_repo.get_user_by_email(form_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_repo.get_user_by_username(form_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(form_data.password)
    user = DomainUser(
        username=form_data.name,
        email=form_data.email,
        full_name=form_data.name,
        hashed_password=hashed_password,
        role="user",
        is_superuser=False,
        is_active=True
    )
    
    user = user_repo.create_user(user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role, "is_superuser": user.is_superuser},
        expires_delta=access_token_expires
    )
    
    return ApiResponse(
        success=True,
        message="Registration successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_domain(user)
        },
    )

@router.get("/me", response_model=ApiResponse, tags=["Auth"])
async def get_current_user_info(current_user: DomainUser = Depends(get_current_user)):
    """Get current user information."""
    return ApiResponse(
        success=True,
        message="User retrieved successfully",
        data=UserResponse.from_domain(current_user)
    )

@router.post("/forgot-password", response_model=ApiResponse, tags=["Auth"])
async def forgot_password(form_data: ForgotPasswordForm):
    """Send password reset link to user email."""
    # In a real implementation, you would:
    # 1. Check if user exists
    # 2. Generate a password reset token
    # 3. Send email with reset link
    
    # For now, just return a success message
    return ApiResponse(
        success=True,
        message="If the email exists, a password reset link has been sent",
        data={},
    )

@router.post("/logout", response_model=ApiResponse, tags=["Auth"])
async def logout():
    """Logout user (client-side token removal)."""
    return ApiResponse(
        success=True,
        message="Logged out successfully",
        data={},
    )