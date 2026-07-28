"""
Dependency Injection configuration.
"""

from typing import Final

from app.application.services.incident_service import IncidentService
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)

incident_repository: Final = InMemoryIncidentRepository()
incident_service: Final = IncidentService(incident_repository)


def get_incident_service() -> IncidentService:
    """Return the singleton IncidentService instance."""
    return incident_service