"""
Request DTOs for Incident APIs.
"""

from pydantic import BaseModel, Field

from app.domain.entities.incident import IncidentSeverity


class CreateIncidentRequest(BaseModel):
    """
    DTO used when creating a new incident.
    """

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        examples=["Database Down"],
    )

    description: str = Field(
        ...,
        min_length=5,
        examples=["Primary PostgreSQL database is unavailable."],
    )

    severity: IncidentSeverity

    source: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Grafana"],
    )