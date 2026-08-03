"""
Google ADK orchestrator.

Coordinates a group of `AdkAgent` instances by reusing the
shared `AgentOrchestrator`. The orchestrator accepts a list of
agents (or an `AgentRegistry`) and runs them in order while
sharing a single `AgentContext`, mirroring the behaviour of the
native orchestrator.
"""

from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_registry import AgentRegistry
from app.application.agents.agent_result import (
    AgentResult,
)
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)
from app.infrastructure.adk.adk_agent import AdkAgent


class AdkOrchestrator:
    """
    Runs ADK-backed agents through the shared orchestration
    pipeline.

    Agents may be supplied as a ready-made `AgentRegistry` or as
    a list of `AdkAgent` instances (which are registered into a
    fresh registry by name).
    """

    def __init__(
        self,
        agents: list[AdkAgent] | None = None,
        registry: AgentRegistry | None = None,
        stop_on_failure: bool = True,
    ) -> None:

        self.registry = registry or AgentRegistry()

        for agent in agents or []:
            self.registry.register(agent)

        self._orchestrator = AgentOrchestrator(
            registry=self.registry,
            stop_on_failure=stop_on_failure,
        )

    def register(
        self,
        agent: Agent,
    ) -> None:
        self.registry.register(agent)

    def list_agents(self) -> list[str]:
        return self.registry.list()

    def agent_count(self) -> int:
        return len(self.registry)

    async def run(
        self,
        context: AgentContext,
        agent_names: list[str] | None = None,
    ) -> list[AgentResult]:

        return await self._orchestrator.run(
            context,
            agent_names,
        )

    @staticmethod
    def context(
        incident_id: str,
        workflow_id: str,
        input_data: dict | None = None,
    ) -> AgentContext:

        return AgentContext(
            incident_id=incident_id,
            workflow_id=workflow_id,
            input=input_data or {},
        )
