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


class SlackTool(Tool):
    """
    Slack integration.

    Action: send_message.
    """

    def __init__(
        self,
        endpoint: str = "https://slack.com/api",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="slack",
                category=ToolCategory.SLACK,
                description=(
                    "Slack message notification."
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
            tool="slack",
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
                f"Unsupported Slack action '{action}'.",
                )

        status, data = await self.transport.request(
            "POST",
            f"{self.endpoint}/chat.postMessage",
            json={
                "channel": parameters.get("channel"),
                "text": parameters.get("message"),
            },
        )

        if status >= 400:
            return self._failure(
                f"Slack send message failed: {data}",
            )

        return ToolResult(
            tool="slack",
            success=True,
            data={
                "action": "send_message",
                "response": data,
            },
        )
