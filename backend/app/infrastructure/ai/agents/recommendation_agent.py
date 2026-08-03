from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class RecommendationAgent(Agent):
    """
    Builds final recommendations from collected agent
    outputs stored in the shared context.
    """

    def __init__(self) -> None:

        super().__init__(
            AgentMetadata(
                name="recommendation",
                description="Aggregates remediation recommendations.",
                order=3,
            )
        )

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        analysis = context.get("analysis", {})

        recommendations = list(
            context.recommendations
        )

        if analysis and analysis.get("recommendation"):

            if analysis["recommendation"] not in recommendations:
                recommendations.append(
                    analysis["recommendation"]
                )

        context.set(
            "final_recommendations",
            recommendations,
        )

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "recommendations": recommendations,
                "count": len(recommendations),
            },
        )
