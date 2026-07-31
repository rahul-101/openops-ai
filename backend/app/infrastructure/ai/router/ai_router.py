from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.core.logging import logger
from app.core.request_context import request_id_ctx
from app.infrastructure.ai.registry.provider_registry import ProviderRegistry
from app.infrastructure.ai.routing.routing_policy import RoutingPolicy
from app.infrastructure.ai.exceptions import (
    RetryableProviderError,
    NonRetryableProviderError,
)


class AIRouter(AIService):
    """
    Routes AI requests using the configured routing policy.
    Supports intelligent provider failover.
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

        log = logger.bind(
            request_id=request_id_ctx.get(),
        )

        providers = self.routing_policy.get_provider_priority()

        last_exception = None

        for provider_name in providers:

            provider = self.registry.get(provider_name)

            log.info(
                "Trying AI provider",
                provider=provider_name,
            )

            try:

                response = await provider.analyze_incident(
                    request=request,
                    prompt=prompt,
                )

                log.info(
                    "AI provider succeeded",
                    provider=provider_name,
                )

                return response

            except RetryableProviderError as ex:

                last_exception = ex

                log.warning(
                    "Retryable provider failure. Trying next provider.",
                    provider=provider_name,
                    error=str(ex),
                )

                continue

            except NonRetryableProviderError as ex:

                log.error(
                    "Non-retryable provider failure.",
                    provider=provider_name,
                    error=str(ex),
                )

                raise

        log.error(
            "All AI providers failed.",
        )

        raise RuntimeError(
            "All registered AI providers failed to process the request."
        ) from last_exception