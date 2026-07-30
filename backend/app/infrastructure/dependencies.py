"""
Application dependency providers.
"""

from app.application.services.incident_analysis_service import (
    IncidentAnalysisService,
)
from app.application.services.incident_service import IncidentService
from app.core.config import settings
from app.domain.repositories.incident_repository import IncidentRepository
from app.infrastructure.ai.agents.incident_agent import IncidentAgent
from app.infrastructure.ai.providers.gemini_provider import GeminiProvider
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)
from app.infrastructure.repositories.mongo.mongo_incident_repository import (
    MongoIncidentRepository,
)


# ------------------------------------------------------------------
# Repository
# ------------------------------------------------------------------


def get_incident_repository() -> IncidentRepository:
    """
    Returns the configured repository implementation.
    """

    if settings.REPOSITORY_TYPE.lower() == "mongo":
        return MongoIncidentRepository()

    return InMemoryIncidentRepository()


# ------------------------------------------------------------------
# Incident CRUD Service
# ------------------------------------------------------------------


def get_incident_service() -> IncidentService:
    """
    Returns the Incident CRUD service.
    """

    return IncidentService(
        repository=get_incident_repository(),
    )


# ------------------------------------------------------------------
# AI
# ------------------------------------------------------------------


def get_ai_provider() -> GeminiProvider:
    """
    Returns the configured AI provider.
    """

    return GeminiProvider()


def get_incident_agent() -> IncidentAgent:
    """
    Returns the AI incident agent.
    """

    return IncidentAgent(
        ai_service=get_ai_provider(),
    )


def get_incident_analysis_service() -> IncidentAnalysisService:
    """
    Returns the application service responsible for AI analysis.
    """

    return IncidentAnalysisService(
        agent=get_incident_agent(),
    )