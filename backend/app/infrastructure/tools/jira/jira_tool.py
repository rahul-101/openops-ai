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


class JiraTool(Tool):
    """
    Jira integration.

    Actions: create_issue, update_issue, add_comment,
    transition_status.

    update_issue and transition_status require approval.
    """

    RISKY_ACTIONS = (
        "update_issue",
        "transition_status",
    )

    def __init__(
        self,
        base_url: str = "https://your-domain.atlassian.net",
        email: str = "",
        api_token: str = "",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="jira",
                category=ToolCategory.JIRA,
                description=(
                    "Jira issue management integration."
                ),
            )
        )

        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.transport = transport or HttpxTransport()

    # ==========================================================
    # Execution
    # ==========================================================


    @staticmethod
    def _failure(
        error: str,
    ) -> ToolResult:

        return ToolResult(
            tool="jira",
            success=False,
            error=error,
        )

    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        action = parameters.get("action")

        handlers = {
            "create_issue": self._create_issue,
            "update_issue": self._update_issue,
            "add_comment": self._add_comment,
            "transition_status": self._transition_status,
        }

        handler = handlers.get(action)

        if handler is None:
            return self._failure(
                f"Unsupported Jira action '{action}'.",
                )

        return await handler(parameters)

    # ==========================================================
    # Actions
    # ==========================================================

    async def _create_issue(
        self,
        parameters: dict,
    ) -> ToolResult:

        payload = {
            "fields": {
                "project": {"key": parameters.get("project_key")},
                "summary": parameters.get("summary"),
                "description": parameters.get("description"),
                "issuetype": {"name": parameters.get("issue_type", "Task")},
            }
        }

        status, data = await self._post(
            "/rest/api/2/issue",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"Jira create issue failed: {data}",
            )

        return self._result(
            "create_issue",
            data,
        )

    async def _update_issue(
        self,
        parameters: dict,
    ) -> ToolResult:

        issue_key = parameters.get("issue_key")

        payload = {
            "fields": {
                key: parameters[key]
                for key in ("summary", "description", "labels")
                if key in parameters
            }
        }

        status, data = await self._put(
            f"/rest/api/2/issue/{issue_key}",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"Jira update issue failed: {data}",
            )

        return self._result(
            "update_issue",
            {"issue_key": issue_key},
        )

    async def _add_comment(
        self,
        parameters: dict,
    ) -> ToolResult:

        issue_key = parameters.get("issue_key")

        payload = {
            "body": parameters.get("comment"),
        }

        status, data = await self._post(
            f"/rest/api/2/issue/{issue_key}/comment",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"Jira add comment failed: {data}",
            )

        return self._result(
            "add_comment",
            data,
        )

    async def _transition_status(
        self,
        parameters: dict,
    ) -> ToolResult:

        issue_key = parameters.get("issue_key")

        payload = {
            "transition": {
                "id": parameters.get("transition_id"),
            }
        }

        status, data = await self._post(
            f"/rest/api/2/issue/{issue_key}/transitions",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"Jira transition failed: {data}",
            )

        return self._result(
            "transition_status",
            {"issue_key": issue_key},
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _post(
        self,
        path: str,
        payload: dict,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "POST",
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
        )

    async def _put(
        self,
        path: str,
        payload: dict,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "PUT",
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
        )

    @staticmethod
    def _result(
        action: str,
        data: dict,
    ) -> ToolResult:

        return ToolResult(
            tool="jira",
            success=True,
            data={
                "action": action,
                "response": data,
            },
        )
