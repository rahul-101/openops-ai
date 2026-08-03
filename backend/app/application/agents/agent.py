from abc import ABC, abstractmethod

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import AgentResult


class Agent(ABC):
    """
    Contract for every workflow agent.

    Agents receive a shared context and return a result.
    """

    def __init__(
        self,
        metadata: AgentMetadata,
    ) -> None:
        self.metadata = metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    @abstractmethod
    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:
        raise NotImplementedError
