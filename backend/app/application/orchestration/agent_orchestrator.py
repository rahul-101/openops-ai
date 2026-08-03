from time import perf_counter

from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_registry import AgentRegistry
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class AgentOrchestrator:
    """
    Coordinates execution of multiple agents.

    Agents run in registry order (or a provided explicit
    order). The same context is passed through every agent
    enabling state and recommendation passing.

    When `stop_on_failure` is True, execution halts at the
    first failed agent.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        stop_on_failure: bool = True,
    ) -> None:

        self.registry = registry
        self.stop_on_failure = stop_on_failure

    async def run(
        self,
        context: AgentContext,
        agent_names: list[str] | None = None,
    ) -> list[AgentResult]:

        agents = self._resolve_agents(agent_names)

        history: list[AgentResult] = []

        for agent in agents:

            result = await self._execute_agent(
                agent,
                context,
            )

            history.append(result)

            context.history.append(result)

            if (
                result.status == AgentStatus.FAILURE
                and self.stop_on_failure
            ):
                break

        return history

    # ==========================================================
    # Helpers
    # ==========================================================

    def _resolve_agents(
        self,
        agent_names: list[str] | None,
    ) -> list[Agent]:

        if agent_names is None:
            return self.registry.ordered()

        resolved = []

        for name in agent_names:
            resolved.append(
                self.registry.get(name)
            )

        return resolved

    async def _execute_agent(
        self,
        agent: Agent,
        context: AgentContext,
    ) -> AgentResult:

        start = perf_counter()

        try:

            result = await agent.execute(context)

        except Exception as ex:

            result = AgentResult(
                agent=agent.name,
                status=AgentStatus.FAILURE,
                error=str(ex),
                duration_ms=(
                    perf_counter() - start
                ) * 1000,
            )

        else:

            result.duration_ms = (
                perf_counter() - start
            ) * 1000

        return result
