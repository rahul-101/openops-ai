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


class AWSTool(Tool):
    """
    AWS integration (EC2, CloudWatch, RDS).

    Mutating actions (start/stop instances, reboot RDS)
    require approval.
    """

    RISKY_ACTIONS = (
        "start_instance",
        "stop_instance",
        "reboot_db_instance",
    )

    def __init__(
        self,
        endpoint: str = "https://aws-api.internal",
        transport: HttpTransport | None = None,
    ) -> None:

        super().__init__(
            ToolMetadata(
                name="aws",
                category=ToolCategory.AWS,
                description=(
                    "AWS EC2, CloudWatch and RDS operations."
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
            tool="aws",
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
            "describe_instances": self._describe_instances,
            "start_instance": self._start_instance,
            "stop_instance": self._stop_instance,
            "get_cloudwatch_metrics": self._get_metrics,
            "describe_db_instances": self._describe_db_instances,
            "reboot_db_instance": self._reboot_db_instance,
        }

        handler = handlers.get(action)

        if handler is None:
            return self._failure(
                f"Unsupported AWS action '{action}'.",
                )

        return await handler(parameters)

    # ==========================================================
    # EC2
    # ==========================================================

    async def _describe_instances(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._post(
            "/ec2/describe-instances",
            {"filters": parameters.get("filters")},
        )

        if status >= 400:
            return self._failure(
                f"AWS describe instances failed: {data}",
            )

        return self._result("describe_instances", data)

    async def _start_instance(
        self,
        parameters: dict,
    ) -> ToolResult:

        instance_id = parameters.get("instance_id")

        status, data = await self._post(
            "/ec2/start-instances",
            {"instance_ids": [instance_id]},
        )

        if status >= 400:
            return self._failure(
                f"AWS start instance failed: {data}",
            )

        return self._result(
            "start_instance",
            {"instance_id": instance_id, "response": data},
        )

    async def _stop_instance(
        self,
        parameters: dict,
    ) -> ToolResult:

        instance_id = parameters.get("instance_id")

        status, data = await self._post(
            "/ec2/stop-instances",
            {"instance_ids": [instance_id]},
        )

        if status >= 400:
            return self._failure(
                f"AWS stop instance failed: {data}",
            )

        return self._result(
            "stop_instance",
            {"instance_id": instance_id, "response": data},
        )

    # ==========================================================
    # CloudWatch
    # ==========================================================

    async def _get_metrics(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._post(
            "/cloudwatch/get-metrics",
            {
                "namespace": parameters.get("namespace"),
                "metric_name": parameters.get("metric_name"),
                "period": parameters.get("period", 300),
            },
        )

        if status >= 400:
            return self._failure(
                f"AWS get metrics failed: {data}",
            )

        return self._result("get_cloudwatch_metrics", data)

    # ==========================================================
    # RDS
    # ==========================================================

    async def _describe_db_instances(
        self,
        parameters: dict,
    ) -> ToolResult:

        status, data = await self._post(
            "/rds/describe-db-instances",
            {},
        )

        if status >= 400:
            return self._failure(
                f"AWS describe db instances failed: {data}",
            )

        return self._result("describe_db_instances", data)

    async def _reboot_db_instance(
        self,
        parameters: dict,
    ) -> ToolResult:

        db_instance = parameters.get("db_instance_identifier")

        status, data = await self._post(
            "/rds/reboot-db-instance",
            {"db_instance_identifier": db_instance},
        )

        if status >= 400:
            return self._failure(
                f"AWS reboot db instance failed: {data}",
            )

        return self._result(
            "reboot_db_instance",
            {"db_instance_identifier": db_instance},
        )

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

    @staticmethod
    def _result(
        action: str,
        data: dict,
    ) -> ToolResult:

        return ToolResult(
            tool="aws",
            success=True,
            data={
                "action": action,
                "response": data,
            },
        )
