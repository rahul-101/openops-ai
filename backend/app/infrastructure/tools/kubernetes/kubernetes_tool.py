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


class KubernetesTool(Tool):
    """
    Kubernetes integration.

    Actions: pod_status, logs, restart, scale.

    restart and scale require approval.
    """

    RISKY_ACTIONS = (
        "restart",
        "scale",
    )

    def __init__(
        self,
        endpoint: str = "https://kubernetes.default.svc",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="kubernetes",
                category=ToolCategory.KUBERNETES,
                description=(
                    "Kubernetes pod status, logs, restart and scaling."
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
            tool="kubernetes",
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
            "pod_status": self._pod_status,
            "logs": self._logs,
            "restart": self._restart,
            "scale": self._scale,
        }

        handler = handlers.get(action)

        if handler is None:
            return self._failure(
                f"Unsupported Kubernetes action '{action}'.",
                )

        return await handler(parameters)

    # ==========================================================
    # Actions
    # ==========================================================

    async def _pod_status(
        self,
        parameters: dict,
    ) -> ToolResult:

        namespace = parameters.get("namespace", "default")

        status, data = await self._get(
            f"/api/v1/namespaces/{namespace}/pods",
        )

        if status >= 400:
            return self._failure(
                f"Kubernetes pod status failed: {data}",
            )

        return self._result("pod_status", data)

    async def _logs(
        self,
        parameters: dict,
    ) -> ToolResult:

        namespace = parameters.get("namespace", "default")

        pod = parameters.get("pod_name")

        status, data = await self._get(
            f"/api/v1/namespaces/{namespace}/pods/{pod}/log",
        )

        if status >= 400:
            return self._failure(
                f"Kubernetes logs failed: {data}",
            )

        return self._result("logs", data)

    async def _restart(
        self,
        parameters: dict,
    ) -> ToolResult:

        namespace = parameters.get("namespace", "default")

        deployment = parameters.get("deployment")

        status, data = await self._post(
            f"/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}/restart",
            {},
        )

        if status >= 400:
            return self._failure(
                f"Kubernetes restart failed: {data}",
            )

        return self._result(
            "restart",
            {"deployment": deployment, "namespace": namespace},
        )

    async def _scale(
        self,
        parameters: dict,
    ) -> ToolResult:

        namespace = parameters.get("namespace", "default")

        deployment = parameters.get("deployment")

        replicas = parameters.get("replicas")

        status, data = await self._post(
            f"/apis/apps/v1/namespaces/{namespace}/deployments/{deployment}/scale",
            {"replicas": replicas},
        )

        if status >= 400:
            return self._failure(
                f"Kubernetes scale failed: {data}",
            )

        return self._result(
            "scale",
            {
                "deployment": deployment,
                "replicas": replicas,
            },
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    async def _get(
        self,
        path: str,
    ) -> tuple[int, dict]:

        return await self.transport.request(
            "GET",
            f"{self.endpoint}{path}",
        )

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

    @staticmethod
    def _result(
        action: str,
        data: dict,
    ) -> ToolResult:

        return ToolResult(
            tool="kubernetes",
            success=True,
            data={
                "action": action,
                "response": data,
            },
        )
