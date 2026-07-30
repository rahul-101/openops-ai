import json
import time

from google import genai

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.core.config import settings


class GeminiProvider(AIService):
    """
    Google Gemini implementation.
    """

    MODEL = "gemini-2.5-flash"

    def __init__(self):

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

        start = time.perf_counter()

        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=prompt,
        )

        elapsed = (time.perf_counter() - start) * 1000

        text = response.text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as ex:
            raise ValueError(
                f"Gemini returned invalid JSON:\n{text}"
            ) from ex

        usage = getattr(response, "usage_metadata", None)

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

        return AIResponse(
            summary=data["summary"],
            severity=data["severity"],
            category=data["category"],
            probable_cause=data["probable_cause"],
            recommendation=data["recommendation"],
            confidence=float(data["confidence"]),
            provider="Gemini",
            model=self.MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            processing_time_ms=round(elapsed, 2),
        )