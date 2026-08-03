from abc import ABC, abstractmethod

from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.models import (
    ToolCategory,
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)


class DatabaseAdapter(ABC):
    """
    Abstraction over a database connection.

    Enables mocking in tests.
    """

    @abstractmethod
    async def query(
        self,
        sql: str,
        parameters: dict | None = None,
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        sql: str,
        parameters: dict | None = None,
    ) -> int:
        raise NotImplementedError


class DatabaseTool(Tool):
    """
    Database query and maintenance tool.

    Data-modifying statements (INSERT/UPDATE/DELETE/DDL)
    require approval.
    """

    RISKY_ACTIONS = ("execute",)

    def __init__(
        self,
        adapter: DatabaseAdapter,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="database",
                category=ToolCategory.DATABASE,
                description=(
                    "Database query and statement execution."
                ),
            )
        )

        self.adapter = adapter

    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        action = parameters.get("action")

        sql = parameters.get("sql")

        if action == "query":

            rows = await self.adapter.query(sql)

            return ToolResult(
                tool="database",
                success=True,
                data={
                    "action": "query",
                    "rows": rows,
                    "row_count": len(rows),
                },
            )

        if action == "execute":

            affected = await self.adapter.execute(sql)

            return ToolResult(
                tool="database",
                success=True,
                data={
                    "action": "execute",
                    "affected_rows": affected,
                },
            )

        return ToolResult(
            tool="database",
            success=False,
            error=(
                f"Unsupported database action '{action}'."
            ),
        )
