from fastapi import APIRouter

from app.api.models.api_response import ApiResponse
from app.core.exceptions import ResourceNotFoundException

router = APIRouter()


@router.get("/", response_model=ApiResponse, tags=["Root"])
def root():
    return ApiResponse(
        success=True,
        message="Welcome to OpenOps AI",
        data={
            "status": "running",
        },
    )


@router.get("/health", response_model=ApiResponse, tags=["Health"])
def health():
    return ApiResponse(
        success=True,
        message="Health check successful",
        data={
            "status": "healthy",
        },
    )


@router.get("/demo-error", response_model=ApiResponse, tags=["Demo"])
def demo_error():
    raise ResourceNotFoundException("Incident")
