import json
import time
from asyncio import sleep

from google.genai import errors as genai_errors

from app.infrastructure.ai.exceptions import (
    AuthenticationError,
    InvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

from google import genai
from pydantic import ValidationError

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.core.config import settings
from app.core.logging import logger
from app.core.request_context import request_id_ctx
from app.infrastructure.ai.models.gemini_response import GeminiResponse


class GeminiProvider(AIService):
    """
    Google Gemini implementation with retry support,
    structured logging and request tracing.
    """

    MODEL = "gemini-2.5-flash"
    PROVIDER = "Gemini"

    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def analyze_incident(
        self,
        request: IncidentRequest,
        prompt: str,
    ) -> AIResponse:

        log = logger.bind(
            request_id=request_id_ctx.get(),
            provider=self.PROVIDER,
            model=self.MODEL,
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

                response = self.client.models.generate_content(
                    model=self.MODEL,
                    contents=prompt,
                )

                text = getattr(response, "text", None)

                if not text or not text.strip():
                    raise InvalidRequestError(
                        "Gemini returned an empty response."
                    )

                try:
                    raw_data = json.loads(text)

                except json.JSONDecodeError as ex:
                    raise InvalidRequestError(
                        f"Gemini returned invalid JSON:\n{text}"
                    )from ex

                try:
                    parsed = GeminiResponse.model_validate(raw_data)

                except ValidationError as ex:
                    raise InvalidRequestError(
                        f"Gemini response validation failed:\n{ex}"
                    ) from ex

                usage = getattr(
                    response,
                    "usage_metadata",
                    None,
                )

                input_tokens = 0
                output_tokens = 0

                if usage:

                    input_tokens = getattr(
                        usage,
                        "prompt_token_count",
                        0,
                    )

                    output_tokens = getattr(
                        usage,
                        "candidates_token_count",
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
                    model=self.MODEL,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    processing_time_ms=elapsed,
                )

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

                    #
                    # Map provider exceptions into our domain exceptions.
                    #

                    if isinstance(ex, genai_errors.ClientError):

                        status = getattr(ex, "code", None)

                        if status == 401:
                            raise AuthenticationError(str(ex)) from ex

                        if status == 400:
                            raise InvalidRequestError(str(ex)) from ex

                        if status == 429:
                            raise ProviderRateLimitError(str(ex)) from ex

                        if status in (500, 502, 503, 504):
                            raise ProviderUnavailableError(str(ex)) from ex

                    if isinstance(ex, TimeoutError):
                        raise ProviderTimeoutError(str(ex)) from ex

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