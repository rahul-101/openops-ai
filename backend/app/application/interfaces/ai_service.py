from abc import ABC, abstractmethod

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse


class AIService(ABC):
    """
    Contract for all AI providers.

    Every provider (Gemini, OpenRouter, OmniRouter, etc.)
    must implement this interface.
    """

    @abstractmethod
    async def analyze_incident(
        self,
        request: IncidentRequest,
    ) -> AIResponse:
        """
        Analyze an incident and return a structured response.
        """
        raise NotImplementedError