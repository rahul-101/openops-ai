"""
Query DTO for listing incidents.
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.entities.incident import (
    IncidentSeverity,
    IncidentStatus,
)


class IncidentQuery(BaseModel):
    """DTO representing incident list query parameters."""

    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-based).",
    )

    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size.",
    )

    status: IncidentStatus | None = None

    severity: IncidentSeverity | None = None

    source: str | None = None

    search: str | None = None

    sort_by: Literal[
        "created_at",
        "updated_at",
        "title",
        "severity",
        "status",
    ] = "created_at"

    order: Literal[
        "asc",
        "desc",
    ] = "desc"
