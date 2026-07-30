from app.infrastructure.ai.registry.provider_registry import ProviderRegistry
from app.infrastructure.ai.routing.routing_policy import RoutingPolicy


class PriorityRoutingPolicy(RoutingPolicy):
    """
    Selects the highest-priority available provider.

    Current priority:
        1. Gemini
        2. OpenRouter
        3. OmniRouter

    Future versions can make this decision based on
    health, latency, quotas, or cost.
    """

    PRIORITY = [
        "gemini",
        "openrouter",
        "omnirouter",
    ]

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def select_provider(self) -> str:
        for provider in self.PRIORITY:
            if self.registry.exists(provider):
                return provider

        raise RuntimeError("No AI providers are registered.")