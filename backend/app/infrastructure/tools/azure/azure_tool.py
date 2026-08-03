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


class AzureTool(Tool):
    """
    Azure integration (VM, Monitor, Log Analytics).

    VM start/stop actions require approval.
    """

    RISKY_ACTIONS = (
        "start_vm",
        "stop_vm",
    )

    def __init__(
        self,
        endpoint: str = "https://management.azure.com",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="azure",
                category=ToolCategory.AZURE,
                description=(
                    "Azure VM, Monitor and Log Analytics operations."
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
            tool="azure",
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
            "get_vm": self._get_vm,
            "start_vm": self._start_vm,
            "stop_vm": self._stop_vm,
            "get_metrics": self._get_metrics,
            "run_log_analytics_query": self._run_query,
        }

        handler = handlers.get(action)

        if handler is None:
            return self._failure(
                f"Unsupported Azure action '{action}'.",
                )

        return await handler(parameters)

    # ==========================================================
    # VM
    # ==========================================================

    async def _get_vm(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._get(
            "/vm",
            parameters,
        )

        if status >= 400:
            return self._failure(
                f"Azure get vm failed: {data}",
            )

        return self._result("get_vm", data)

    async def _start_vm(
        self,
        parameters: dict,
    ) -> ToolResult:

        vm_name = parameters.get("vm_name")

        status, data = await self._post(
            "/vm/start",
            {"vm_name": vm_name},
        )

        if status >= 400:
            return self._failure(
                f"Azure start vm failed: {data}",
            )

        return self._result(
            "start_vm",
            {"vm_name": vm_name},
        )

    async def _stop_vm(
        self,
        parameters: dict,
    ) -> ToolResult:

        vm_name = parameters.get("vm_name")

        status, data = await self._post(
            "/vm/stop",
            {"vm_name": vm_name},
        )

        if status >= 400:
            return self._failure(
                f"Azure stop vm failed: {data}",
            )

        return self._result(
            "stop_vm",
            {"vm_name": vm_name},
        )

    # ==========================================================
    # Monitor
    # ==========================================================

    async def _get_metrics(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._get(
            "/monitor/metrics",
            parameters,
        )

        if status >= 400:
            return self._failure(
                f"Azure get metrics failed: {data}",
            )

        return self._result("get_metrics", data)

    # ==========================================================
    # Log Analytics
    # ==========================================================

    async def _run_query(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._post(
            "/log-analytics/query",
            {
                "workspace_id": parameters.get("workspace_id"),
                "query": parameters.get("query"),
            },
        )

        if status >= 400:
            return self._failure(
                f"Azure log analytics query failed: {data}",
            )

        return self._result("run_log_analytics_query", data)

    # ==========================================================
    # Helpers
    # ==========================================================

    async def _post(
        self,
        path: str,
        payload: dict,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "POST",
            f"{self.endpoint}{path}",
            json=payload,
        )

    async def _get(
        self,
        path: str,
        parameters: dict,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "GET",
            f"{self.endpoint}{path}",
            params=parameters,
        )

    @staticmethod
    def _result(
        action: str,
        data: dict,
    ) -> ToolResult:

        return ToolResult(
            tool="azure",
            success=True,
            data={
                "action": action,
                "response": data,
            },
        )
