from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.models import (
    ToolCategory,
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)
from app.infrastructure.tools.transport import (
    HttpTransport,
    HttpxTransport,
)


class TeamsTool(Tool):
    """
    Microsoft Teams integration.

    Action: send_message.
    """

    def __init__(
        self,
        endpoint: str = "https://graph.microsoft.com/v1.0",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="teams",
                category=ToolCategory.TEAMS,
                description=(
                    "Microsoft Teams message notification."
                ),
            )
        )

        self.endpoint = endpoint.rstrip("/")
        self.transport = transport or HttpxTransport()


    @staticmethod
    def _failure(
        error: str,
    ) -> ToolResult:

        return ToolResult(
            tool="teams",
            success=False,
            error=error,
        )

    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        action = parameters.get("action")

        if action != "send_message":
            return self._failure(
                f"Unsupported Teams action '{action}'.",
                )

        status, data = await self.transport.request(
            "POST",
            f"{self.endpoint}/teams/{parameters.get('team_id')}/channels/{parameters.get('channel_id')}/messages",
            json={
                "body": {"content": parameters.get("message")},
            },
        )

        if status >= 400:
            return self._failure(
                f"Teams send message failed: {data}",
            )

        return ToolResult(
            tool="teams",
            success=True,
            data={
                "action": "send_message",
                "response": data,
            },
        )
