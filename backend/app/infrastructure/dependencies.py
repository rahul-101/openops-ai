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
from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)
from app.infrastructure.ai.router.ai_router import AIRouter
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)
from app.infrastructure.repositories.mongo.mongo_incident_repository import (
    MongoIncidentRepository,
)
from functools import lru_cache
from app.infrastructure.ai.providers.openrouter_provider import (
    OpenRouterProvider,
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
# AI Providers
# ------------------------------------------------------------------

from functools import lru_cache

from app.infrastructure.ai.routing.priority_routing_policy import (
    PriorityRoutingPolicy,
)


@lru_cache
def get_gemini_provider() -> GeminiProvider:
    return GeminiProvider()


@lru_cache
def get_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()

    registry.register(
        "gemini",
        get_gemini_provider(),
    )

    registry.register(
        "openrouter",
        get_openrouter_provider(),
    )

    return registry


@lru_cache
def get_routing_policy() -> PriorityRoutingPolicy:
    return PriorityRoutingPolicy(
        registry=get_provider_registry(),
    )


@lru_cache
def get_ai_router() -> AIRouter:
    return AIRouter(
        registry=get_provider_registry(),
        routing_policy=get_routing_policy(),
    )


@lru_cache
def get_incident_agent() -> IncidentAgent:
    return IncidentAgent(
        ai_service=get_ai_router(),
    )


@lru_cache
def get_incident_analysis_service() -> IncidentAnalysisService:
    return IncidentAnalysisService(
        agent=get_incident_agent(),
    )

@lru_cache
def get_openrouter_provider() -> OpenRouterProvider:
    return OpenRouterProvider()