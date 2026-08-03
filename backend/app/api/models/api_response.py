from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    message: str
    data: Any | None = None
