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

        providers = self.routing_policy.get_provider_priority()

        last_exception = None

        for provider_name in providers:
            provider = self.registry.get(provider_name)

            try:
                return await provider.analyze_incident(
                    request=request,
                    prompt=prompt,
                )

            except Exception as ex:
                last_exception = ex

                print(
                    f"[AI Router] Provider '{provider_name}' failed. "
                    f"Trying next provider..."
                )

                continue

        raise RuntimeError(
            "All registered AI providers failed to process the request."
        ) from last_exception