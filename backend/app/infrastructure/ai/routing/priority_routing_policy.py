from app.infrastructure.ai.registry.provider_registry import ProviderRegistry
from app.infrastructure.ai.routing.routing_policy import RoutingPolicy


class PriorityRoutingPolicy(RoutingPolicy):
    """
    Selects the highest-priority available provider.

    Current priority:
        1. Gemini
        2. OpenRouter

    Future versions can make this decision based on
    health, latency, quotas, or cost.
    """

    PRIORITY = [
        "gemini",
        "openrouter",
    ]

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def get_provider_priority(self) -> list[str]:
        """
        Returns all registered providers in priority order.
        """
        providers = [
            provider
            for provider in self.PRIORITY
            if self.registry.exists(provider)
        ]

        if not providers:
            raise RuntimeError("No AI providers are registered.")

        return providers