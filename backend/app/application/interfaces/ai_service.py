from abc import ABC, abstractmethod

from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse


class AIService(ABC):
    """
    Contract for every AI provider.
    """

    @abstractmethod
    async def analyze_incident(
        self,
        request: IncidentRequest,
        prompt: str,
    ) -> AIResponse:
        """
        Analyze an incident using the rendered prompt.
        """
        raise NotImplementedError