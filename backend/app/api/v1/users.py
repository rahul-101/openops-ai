from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.api.models.api_response import ApiResponse
from app.infrastructure.auth.types import User as DomainUser
from app.infrastructure.persistence.user_repository import get_user_repository
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=ApiResponse)
async def get_users(current_user: DomainUser = Depends(get_current_user)):
    """Get all users (admin/operator only)."""
    if not current_user.has_permission("read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view users"
        )
    
    user_repo = get_user_repository()
    users = user_repo.list_users()
    
    return ApiResponse(
        success=True,
        message="Users retrieved successfully",
        data=[{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        } for u in users]
    )

@router.patch("/{user_id}/role", response_model=ApiResponse)
async def update_user_role(
    user_id: str,
    role: str,
    current_user: DomainUser = Depends(get_current_user)
):
    """Update user role (admin only)."""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update user roles"
        )
    
    user_repo = get_user_repository()
    user = user_repo.get_user_by_username(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    valid_roles = ["user", "viewer", "operator", "admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    user.role = role
    user.updated_at = datetime.utcnow()
    user_repo.update_user(user)
    
    return ApiResponse(
        success=True,
        message="User role updated successfully",
        data={
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    )

@router.post("/{user_id}/suspend", response_model=ApiResponse)
async def suspend_user(
    user_id: str,
    current_user: DomainUser = Depends(get_current_user)
):
    """Suspend a user (admin only)."""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to suspend users"
        )
    
    user_repo = get_user_repository()
    user = user_repo.get_user_by_username(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    user_repo.update_user(user)
    
    return ApiResponse(
        success=True,
        message="User suspended successfully",
        data={"id": user.id, "username": user.username}
    )

@router.post("/invite", response_model=ApiResponse)
async def invite_user(
    email: str,
    role: str,
    full_name: str = None,
    current_user: DomainUser = Depends(get_current_user)
):
    """Invite a new user (admin only)."""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to invite users"
        )
    
    user_repo = get_user_repository()
    
    if user_repo.get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    valid_roles = ["user", "viewer", "operator", "admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    # Create invited user (inactive until they accept)
    user = DomainUser(
        username=email.split("@")[0],
        email=email,
        full_name=full_name or email.split("@")[0],
        hashed_password="",  # Will be set when they accept invite
        role=role,
        is_superuser=False,
        is_active=False  # Inactive until they accept invitation
    )
    
    user = user_repo.create_user(user)
    
    return ApiResponse(
        success=True,
        message="User invited successfully",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": "invited"
        }
    )