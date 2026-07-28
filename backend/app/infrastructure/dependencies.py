"""
Dependency Injection configuration.
"""

from functools import lru_cache

from app.application.services.incident_service import IncidentService
from app.core.config import settings
from app.domain.repositories.incident_repository import IncidentRepository
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)


@lru_cache
def get_incident_repository() -> IncidentRepository:
    """
    Return the configured repository implementation.

    Additional repository types (e.g. MongoDB) can be added here
    without changing the application layer.
    """

    match settings.REPOSITORY_TYPE.lower():
        case "memory":
            return InMemoryIncidentRepository()

        case _:
            raise ValueError(
                f"Unsupported repository type: {settings.REPOSITORY_TYPE}"
            )


@lru_cache
def get_incident_service() -> IncidentService:
    """
    Return the singleton IncidentService instance.
    """
    return IncidentService(get_incident_repository())