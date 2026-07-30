from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService


class IncidentAgent:
    """
    Coordinates AI-powered incident analysis.

    The agent is intentionally lightweight.
    It prepares the request and delegates the
    actual AI work to the configured AI provider.
    """

    def __init__(self, ai_service: AIService):
        self._ai_service = ai_service

    async def analyze(
        self,
        title: str,
        description: str,
        severity: str,
    ) -> AIResponse:
        """
        Analyze an incident using the configured AI provider.
        """

        request = IncidentRequest(
            title=title,
            description=description,
            severity=severity,
        )

        return await self._ai_service.analyze_incident(request)