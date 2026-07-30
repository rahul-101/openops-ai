from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.infrastructure.ai.registry.provider_registry import ProviderRegistry
from app.infrastructure.ai.routing.routing_policy import RoutingPolicy


class AIRouter(AIService):
    """
    Routes AI requests using a routing policy.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        routing_policy: RoutingPolicy,
    ) -> None:
        self.registry = registry
        self.routing_policy = routing_policy

    async def analyze_incident(
        self,
        request: IncidentRequest,
        prompt: str,
    ) -> AIResponse:

        provider_name = self.routing_policy.select_provider()

        provider = self.registry.get(provider_name)

        return await provider.analyze_incident(
            request=request,
            prompt=prompt,
        )