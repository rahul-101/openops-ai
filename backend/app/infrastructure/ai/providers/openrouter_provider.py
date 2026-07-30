import json
import time
from asyncio import sleep

import httpx
from pydantic import ValidationError

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.core.config import settings
from app.core.logging import logger
from app.core.request_context import request_id_ctx
from app.infrastructure.ai.models.gemini_response import GeminiResponse


class OpenRouterProvider(AIService):
    """
    OpenRouter implementation with retry support,
    structured logging and request tracing.
    """

    PROVIDER = "OpenRouter"

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0

    def __init__(self) -> None:

        if not settings.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL

    async def analyze_incident(
        self,
        request: IncidentRequest,
        prompt: str,
    ) -> AIResponse:

        log = logger.bind(
            request_id=request_id_ctx.get(),
            provider=self.PROVIDER,
            model=self.model,
        )

        log.info(
            "AI analysis started",
            severity=request.severity,
        )

        start = time.perf_counter()

        last_exception = None

        for attempt in range(self.MAX_RETRIES):

            try:

                log.info(
                    "Calling AI provider",
                    attempt=attempt + 1,
                )

                async with httpx.AsyncClient(
                    timeout=60,
                ) as client:

                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt,
                                }
                            ],
                        },
                    )

                response.raise_for_status()

                payload = response.json()

                text = payload["choices"][0]["message"]["content"]

                raw_data = json.loads(text)

                parsed = GeminiResponse.model_validate(
                    raw_data
                )

                usage = payload.get(
                    "usage",
                    {},
                )

                input_tokens = usage.get(
                    "prompt_tokens",
                    0,
                )

                output_tokens = usage.get(
                    "completion_tokens",
                    0,
                )

                elapsed = round(
                    (time.perf_counter() - start) * 1000,
                    2,
                )

                log.info(
                    "AI analysis completed",
                    severity=parsed.severity,
                    category=parsed.category,
                    confidence=parsed.confidence,
                    latency_ms=elapsed,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

                return AIResponse(
                    summary=parsed.summary,
                    severity=parsed.severity,
                    category=parsed.category,
                    probable_cause=parsed.probable_cause,
                    recommendation=parsed.recommendation,
                    confidence=parsed.confidence,
                    provider=self.PROVIDER,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    processing_time_ms=elapsed,
                )

            except ValidationError as ex:
                raise ValueError(
                    f"Response validation failed:\n{ex}"
                ) from ex

            except Exception as ex:

                last_exception = ex

                log.warning(
                    "AI request failed",
                    attempt=attempt + 1,
                    error=str(ex),
                )

                if attempt == self.MAX_RETRIES - 1:

                    log.exception(
                        "AI analysis failed after maximum retries",
                    )

                    raise

                backoff = self.INITIAL_BACKOFF * (
                    2**attempt
                )

                log.info(
                    "Retrying AI request",
                    next_retry_in_seconds=backoff,
                )

                await sleep(backoff)

        raise last_exception