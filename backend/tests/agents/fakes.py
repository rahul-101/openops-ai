from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)


class FakeAgent(Agent):
    """
    Deterministic test agent.

    `fail` forces every execution to fail.
    `fail_times` fails only the first N executions.
    """

    def __init__(
        self,
        name: str,
        order: int = 100,
        fail: bool = False,
        fail_times: int = 0,
    ) -> None:

        super().__init__(
            AgentMetadata(
                name=name,
                description=f"fake {name}",
                order=order,
            )
        )

        self.fail = fail
        self.fail_times = fail_times
        self.calls = 0

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        self.calls += 1

        if self.fail or self.calls <= self.fail_times:

            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error="boom",
            )

        context.set(
            self.name,
            "done",
        )

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={"name": self.name},
        )
