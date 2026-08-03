from abc import ABC, abstractmethod

from app.infrastructure.tools.models import (
    ToolMetadata,
    ToolResult,
    ToolExecutionContext,
)


class Tool(ABC):
    """
    Contract for every integration tool.
    """

    #: Actions that must be approved before execution.
    RISKY_ACTIONS: tuple = ()

    def __init__(
        self,
        metadata: ToolMetadata,
    ) -> None:

        self.metadata = metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    def requires_approval(
        self,
        parameters: dict,
    ) -> bool:
        """
        Whether the given action needs approval.
        """

        return (
            parameters.get("action")
            in self.RISKY_ACTIONS
        )

    @abstractmethod
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:
        raise NotImplementedError
