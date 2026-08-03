from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.exceptions import (
    ToolNotFoundError,
)


class ToolRegistry:
    """
    Stores and manages all registered tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        tool: Tool,
    ) -> None:
        self._tools[tool.name.lower()] = tool

    def get(
        self,
        name: str,
    ) -> Tool:

        tool = self._tools.get(name.lower())

        if tool is None:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered."
            )

        return tool

    def exists(
        self,
        name: str,
    ) -> bool:
        return name.lower() in self._tools

    def list(self) -> list[str]:
        return sorted(self._tools.keys())

    def by_category(
        self,
        category,
    ) -> list[Tool]:

        return [
            tool
            for tool in self._tools.values()
            if tool.metadata.category == category
        ]

    def __len__(self) -> int:
        return len(self._tools)
