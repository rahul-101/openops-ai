from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class TriageAgent(Agent):
    """
    Rule-based triage agent.

    Classifies the incident and seeds shared context
    state for downstream agents.
    """

    def __init__(self) -> None:

        super().__init__(
            AgentMetadata(
                name="triage",
                description="Classifies incident severity and category.",
                order=1,
            )
        )

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        title = context.input.get("title", "")

        description = context.input.get("description", "")

        severity = context.input.get("severity", "LOW")

        category = self._categorize(
            title,
            description,
        )

        context.set("category", category)

        context.set("severity", severity)

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "category": category,
                "severity": severity,
            },
        )

    @staticmethod
    def _categorize(
        title: str,
        description: str,
    ) -> str:

        text = f"{title} {description}".lower()

        keywords = {
            "database": "database",
            "db": "database",
            "network": "network",
            "latency": "network",
            "security": "security",
            "auth": "security",
            "memory": "infrastructure",
            "cpu": "infrastructure",
            "disk": "infrastructure",
        }

        for keyword, category in keywords.items():
            if keyword in text:
                return category

        return "unknown"
