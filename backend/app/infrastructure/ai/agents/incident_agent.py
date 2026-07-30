from app.application.dto.requests.incident_request import IncidentRequest
from app.application.dto.responses.ai_response import AIResponse
from app.application.interfaces.ai_service import AIService
from app.infrastructure.ai.prompt_manager import PromptManager


class IncidentAgent:
    """
    AI-powered incident analysis agent.
    """

    def __init__(
        self,
        ai_service: AIService,
    ):
        self.ai_service = ai_service
        self.prompt_manager = PromptManager()

    async def analyze(
        self,
        title: str,
        description: str,
        severity: str,
    ) -> AIResponse:

        request = IncidentRequest(
            title=title,
            description=description,
            severity=severity,
        )

        prompt = self.prompt_manager.render_prompt(
            "incident_analysis",
            title=title,
            description=description,
            severity=severity,
        )

        return await self.ai_service.analyze_incident(
            request=request,
            prompt=prompt,
        )