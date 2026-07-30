"""
Application service responsible for AI incident analysis.
"""

from app.application.dto.responses.ai_response import AIResponse
from app.infrastructure.ai.agents.incident_agent import IncidentAgent


class IncidentAnalysisService:
    """
    Coordinates AI-powered incident analysis.
    """

    def __init__(
        self,
        agent: IncidentAgent,
    ) -> None:
        self._agent = agent

    async def analyze(
        self,
        title: str,
        description: str,
        severity: str,
    ) -> AIResponse:
        """
        Analyze an incident using the configured AI provider.
        """

        return await self._agent.analyze(
            title=title,
            description=description,
            severity=severity,
        )