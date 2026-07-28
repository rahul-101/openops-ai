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
from app.infrastructure.repositories.mongo.mongo_incident_repository import (
    MongoIncidentRepository,
)


@lru_cache
def get_incident_repository() -> IncidentRepository:
    """
    Return the configured repository implementation.
    """

    repository_type = settings.REPOSITORY_TYPE.lower()

    if repository_type == "memory":
        return InMemoryIncidentRepository()

    if repository_type == "mongo":
        return MongoIncidentRepository()

    raise ValueError(
        f"Unsupported repository type: {settings.REPOSITORY_TYPE}"
    )


@lru_cache
def get_incident_service() -> IncidentService:
    """
    Return the singleton IncidentService.
    """
    return IncidentService(get_incident_repository())