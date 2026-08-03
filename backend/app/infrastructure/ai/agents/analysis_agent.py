from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)
from app.application.interfaces.ai_service import AIService
from app.application.dto.requests.incident_request import (
    IncidentRequest,
)
from app.infrastructure.ai.prompt_manager import PromptManager


class AnalysisAgent(Agent):
    """
    AI-powered analysis agent.

    Delegates to the existing AI Router via the AIService
    interface and persists the result into shared state.
    """

    def __init__(
        self,
        ai_service: AIService,
        prompt_manager: PromptManager | None = None,
    ) -> None:

        super().__init__(
            AgentMetadata(
                name="analysis",
                description="Analyzes the incident using AI.",
                order=2,
            )
        )

        self.ai_service = ai_service
        self.prompt_manager = (
            prompt_manager or PromptManager()
        )

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        request = IncidentRequest(
            title=context.input.get("title", ""),
            description=context.input.get(
                "description",
                "",
            ),
            severity=context.input.get(
                "severity",
                "LOW",
            ),
        )

        prompt = self.prompt_manager.render_prompt(
            "incident_analysis",
            title=request.title,
            description=request.description,
            severity=request.severity,
        )

        response = await self.ai_service.analyze_incident(
            request=request,
            prompt=prompt,
        )

        output = response.model_dump()

        context.set(
            "analysis",
            output,
        )

        context.add_recommendation(
            output.get("recommendation", "")
        )

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output=output,
        )
