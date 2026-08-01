from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)
from app.infrastructure.ai.routing.routing_engine import (
    RoutingEngine,
)
from app.infrastructure.ai.routing.routing_policy import (
    RoutingPolicy,
)


class PriorityRoutingPolicy(RoutingPolicy):
    """
    Determines the order in which AI providers
    should be attempted.

    The actual ranking logic is delegated to
    the RoutingEngine.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        routing_engine: RoutingEngine,
    ) -> None:

        self.registry = registry
        self.routing_engine = routing_engine

    def get_provider_priority(
        self,
    ) -> list[str]:
        """
        Returns providers ordered by routing score.

        If no providers are returned by the routing engine,
        fall back to the registry order.
        """

        providers = self.routing_engine.rank_providers()

        if providers:
            return providers

        return self.registry.list()