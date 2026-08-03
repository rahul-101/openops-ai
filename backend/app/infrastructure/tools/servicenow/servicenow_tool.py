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


class ServiceNowTool(Tool):
    """
    ServiceNow integration.

    Actions: create_incident, get_incident, update_incident,
    add_work_notes, assign_incident, resolve_incident,
    create_change_request.

    Mutating actions require approval.
    """

    RISKY_ACTIONS = (
        "update_incident",
        "assign_incident",
        "resolve_incident",
        "create_change_request",
    )

    def __init__(
        self,
        instance: str = "https://dev.service-now.com",
        username: str = "",
        password: str = "",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="servicenow",
                category=ToolCategory.SERVICENOW,
                description=(
                    "ServiceNow incident and change request management."
                ),
            )
        )

        self.instance = instance.rstrip("/")
        self.username = username
        self.password = password
        self.transport = transport or HttpxTransport()

    # ==========================================================
    # Execution
    # ==========================================================


    @staticmethod
    def _failure(
        error: str,
    ) -> ToolResult:

        return ToolResult(
            tool="servicenow",
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
            "create_incident": self._create_incident,
            "get_incident": self._get_incident,
            "update_incident": self._update_incident,
            "add_work_notes": self._add_work_notes,
            "assign_incident": self._assign_incident,
            "resolve_incident": self._resolve_incident,
            "create_change_request": self._create_change_request,
        }

        handler = handlers.get(action)

        if handler is None:
            return self._failure(
                f"Unsupported ServiceNow action '{action}'.",
                )

        return await handler(parameters)

    # ==========================================================
    # Incident Actions
    # ==========================================================

    async def _create_incident(
        self,
        parameters: dict,
    ) -> ToolResult:

        payload = {
            "short_description": parameters.get("short_description"),
            "description": parameters.get("description"),
            "category": parameters.get("category"),
            "impact": parameters.get("impact", "2"),
            "urgency": parameters.get("urgency", "2"),
        }

        status, data = await self._post(
            "/api/now/table/incident",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow create incident failed: {data}",
            )

        return self._result(
            "create_incident",
            data,
        )

    async def _get_incident(
        self,
        parameters: dict,
    ) -> ToolResult:

        incident_id = parameters.get("incident_id")

        status, data = await self._get(
            f"/api/now/table/incident/{incident_id}"
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow get incident failed: {data}",
            )

        return self._result(
            "get_incident",
            data,
        )

    async def _update_incident(
        self,
        parameters: dict,
    ) -> ToolResult:

        incident_id = parameters.get("incident_id")

        payload = {
            key: parameters[key]
            for key in ("state", "impact", "urgency")
            if key in parameters
        }

        status, data = await self._patch(
            f"/api/now/table/incident/{incident_id}",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow update incident failed: {data}",
            )

        return self._result(
            "update_incident",
            data,
        )

    async def _add_work_notes(
        self,
        parameters: dict,
    ) -> ToolResult:

        incident_id = parameters.get("incident_id")

        payload = {
            "work_notes": parameters.get("notes"),
        }

        status, data = await self._patch(
            f"/api/now/table/incident/{incident_id}",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow add work notes failed: {data}",
            )

        return self._result(
            "add_work_notes",
            data,
        )

    async def _assign_incident(
        self,
        parameters: dict,
    ) -> ToolResult:

        incident_id = parameters.get("incident_id")

        payload = {
            "assignment_group": parameters.get("assignment_group"),
            "assigned_to": parameters.get("assignee"),
        }

        status, data = await self._patch(
            f"/api/now/table/incident/{incident_id}",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow assign incident failed: {data}",
            )

        return self._result(
            "assign_incident",
            data,
        )

    async def _resolve_incident(
        self,
        parameters: dict,
    ) -> ToolResult:

        incident_id = parameters.get("incident_id")

        payload = {
            "state": "6",
            "close_notes": parameters.get("resolution_notes"),
            "close_code": parameters.get("close_code", "Solved (Permanently)"),
        }

        status, data = await self._patch(
            f"/api/now/table/incident/{incident_id}",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow resolve incident failed: {data}",
            )

        return self._result(
            "resolve_incident",
            data,
        )

    # ==========================================================
    # Change Request
    # ==========================================================

    async def _create_change_request(
        self,
        parameters: dict,
    ) -> ToolResult:

        payload = {
            "short_description": parameters.get("short_description"),
            "description": parameters.get("description"),
            "risk": parameters.get("risk", "moderate"),
            "impact": parameters.get("impact", "2"),
            "start_date": parameters.get("start_date"),
            "end_date": parameters.get("end_date"),
        }

        status, data = await self._post(
            "/api/now/table/change_request",
            payload,
        )

        if status >= 400:
            return self._failure(
                f"ServiceNow create change request failed: {data}",
            )

        return self._result(
            "create_change_request",
            data,
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
            f"{self.instance}{path}",
            json=payload,
            headers=self._headers(),
        )

    async def _patch(
        self,
        path: str,
        payload: dict,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "PATCH",
            f"{self.instance}{path}",
            json=payload,
            headers=self._headers(),
        )

    async def _get(
        self,
        path: str,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "GET",
            f"{self.instance}{path}",
            headers=self._headers(),
        )

    @staticmethod
    def _result(
        action: str,
        data: dict,
    ) -> ToolResult:

        return ToolResult(
            tool="servicenow",
            success=True,
            data={
                "action": action,
                "response": data,
            },
        )
