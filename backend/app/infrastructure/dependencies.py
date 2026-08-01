"""
Application dependency providers.
"""

from functools import lru_cache

from app.application.services.incident_analysis_service import (
    IncidentAnalysisService,
)
from app.application.services.incident_service import IncidentService
from app.core.config import settings
from app.domain.repositories.incident_repository import IncidentRepository

from app.infrastructure.ai.agents.incident_agent import IncidentAgent

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.providers.gemini_provider import (
    GeminiProvider,
)

from app.infrastructure.ai.providers.openrouter_provider import (
    OpenRouterProvider,
)

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderCapability,
    ProviderMetadata,
)

from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)

from app.infrastructure.ai.router.ai_router import (
    AIRouter,
)

from app.infrastructure.ai.routing.priority_routing_policy import (
    PriorityRoutingPolicy,
)

from app.infrastructure.ai.routing.provider_scorer import (
    ProviderScorer,
)

from app.infrastructure.ai.routing.routing_engine import (
    RoutingEngine,
)

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

    if settings.REPOSITORY_TYPE.lower() == "mongo":
        return MongoIncidentRepository()

    return InMemoryIncidentRepository()


# ------------------------------------------------------------------
# Incident CRUD Service
# ------------------------------------------------------------------


def get_incident_service() -> IncidentService:

    return IncidentService(
        repository=get_incident_repository(),
    )


# ------------------------------------------------------------------
# AI Providers
# ------------------------------------------------------------------


@lru_cache
def get_gemini_provider() -> GeminiProvider:
    return GeminiProvider()


@lru_cache
def get_openrouter_provider() -> OpenRouterProvider:
    return OpenRouterProvider()


# ------------------------------------------------------------------
# Provider Registry
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# NEW
# Provider Metadata Registry
# ------------------------------------------------------------------


@lru_cache
def get_provider_metadata_registry() -> ProviderMetadataRegistry:

    registry = ProviderMetadataRegistry()

    registry.register(
        ProviderMetadata(
            name="gemini",
            display_name="Google Gemini",
            model="gemini-2.0-flash",
            priority=1,
            input_cost_per_1k_tokens=0.000075,
            output_cost_per_1k_tokens=0.0003,
            max_context_tokens=1_000_000,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                    ProviderCapability.STRUCTURED_OUTPUT,
                    ProviderCapability.FUNCTION_CALLING,
                    ProviderCapability.STREAMING,
                    ProviderCapability.LONG_CONTEXT,
                }
            ),
        )
    )

    registry.register(
        ProviderMetadata(
            name="openrouter",
            display_name="OpenRouter",
            model=settings.OPENROUTER_MODEL,
            priority=2,
            input_cost_per_1k_tokens=0.0,
            output_cost_per_1k_tokens=0.0,
            max_context_tokens=8192,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                    ProviderCapability.STREAMING,
                }
            ),
        )
    )

    return registry


# ------------------------------------------------------------------
# Health Service
# ------------------------------------------------------------------


@lru_cache
def get_provider_health_service() -> ProviderHealthService:

    return ProviderHealthService()


# ------------------------------------------------------------------
# Metrics Service
# ------------------------------------------------------------------


@lru_cache
def get_provider_metrics_service() -> ProviderMetricsService:

    return ProviderMetricsService()


# ------------------------------------------------------------------
# NEW
# Provider Scorer
# ------------------------------------------------------------------


@lru_cache
def get_provider_scorer() -> ProviderScorer:

    return ProviderScorer(
        metadata_registry=get_provider_metadata_registry(),
    )


# ------------------------------------------------------------------
# NEW
# Routing Engine
# ------------------------------------------------------------------


@lru_cache
def get_routing_engine() -> RoutingEngine:

    return RoutingEngine(
        registry=get_provider_registry(),
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
        scorer=get_provider_scorer(),
    )


# ------------------------------------------------------------------
# Routing Policy
# ------------------------------------------------------------------


@lru_cache
def get_routing_policy() -> PriorityRoutingPolicy:

    return PriorityRoutingPolicy(
        registry=get_provider_registry(),
        routing_engine=get_routing_engine(),
    )


# ------------------------------------------------------------------
# AI Router
# ------------------------------------------------------------------


@lru_cache
def get_ai_router() -> AIRouter:

    return AIRouter(
        registry=get_provider_registry(),
        routing_policy=get_routing_policy(),
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
    )


# ------------------------------------------------------------------
# AI Agent
# ------------------------------------------------------------------


@lru_cache
def get_incident_agent() -> IncidentAgent:

    return IncidentAgent(
        ai_service=get_ai_router(),
    )


# ------------------------------------------------------------------
# Incident Analysis Service
# ------------------------------------------------------------------


@lru_cache
def get_incident_analysis_service() -> IncidentAnalysisService:

    return IncidentAnalysisService(
        agent=get_incident_agent(),
    )