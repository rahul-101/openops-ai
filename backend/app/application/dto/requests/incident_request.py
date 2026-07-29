"""
Request DTOs for Incident APIs.
"""

from pydantic import BaseModel, Field

from app.domain.entities.incident import (
    IncidentSeverity,
    IncidentStatus,
)


class CreateIncidentRequest(BaseModel):
    """DTO for creating an incident."""

    title: str = Field(..., min_length=3, max_length=200)

    description: str = Field(..., min_length=5)

    severity: IncidentSeverity

    source: str = Field(..., min_length=2, max_length=100)


class UpdateIncidentRequest(BaseModel):
    """DTO for updating an incident."""

    title: str = Field(..., min_length=3, max_length=200)

    description: str = Field(..., min_length=5)

    severity: IncidentSeverity

    status: IncidentStatus

    source: str = Field(..., min_length=2, max_length=100)