from app.infrastructure.tools.approval import ApprovalWorkflow
from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.exceptions import (
    ToolApprovalDeniedError,
    ToolApprovalRequiredError,
)
from app.infrastructure.tools.models import (
    ToolExecutionContext,
    ToolResult,
)
from app.infrastructure.tools.registry import ToolRegistry
from app.infrastructure.tracing.tracer import Tracer


class ToolExecutor:
    """
    Executes tool actions.

    Risky actions are gated by the approval workflow:
    they raise an approval requirement and only run after
    explicit approval via `execute_approved`.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        approval: ApprovalWorkflow | None = None,
        tracer: Tracer | None = None,
    ) -> None:

        self.registry = registry
        self.approval = approval
        self.tracer = tracer

    async def execute(
        self,
        tool_name: str,
        parameters: dict,
        context: ToolExecutionContext | None = None,
    ) -> ToolResult:

        tool = self.registry.get(tool_name)

        if not tool.requires_approval(parameters):
            return await self._run(tool, parameters, context)

        if self.approval is None:
            raise ToolApprovalRequiredError(
                f"Tool '{tool_name}' requires approval but no "
                "approval workflow is configured."
            )

        approval = self.approval.request(
            tool_name=tool_name,
            parameters=parameters,
            context=self._context_to_dict(context),
        )

        return ToolResult(
            tool=tool_name,
            success=False,
            data={
                "approval_id": approval.id,
                "status": approval.status.value,
            },
            error=(
                "Action requires approval before execution."
            ),
        )

    async def execute_approved(
        self,
        approval_id: str,
    ) -> ToolResult:

        if self.approval is None:
            raise ToolApprovalDeniedError(
                "No approval workflow configured."
            )

        approval = self.approval.get(approval_id)

        if approval is None:
            raise ToolApprovalDeniedError(
                f"Approval '{approval_id}' not found."
            )

        if approval.status.value != "approved":
            raise ToolApprovalDeniedError(
                f"Approval '{approval_id}' is not approved."
            )

        tool = self.registry.get(approval.tool_name)

        result = await self._run(
            tool,
            approval.parameters,
            self._context_from_dict(approval.context),
        )

        self.approval.mark_executed(
            approval_id,
            result.data,
        )

        return result

    # ==========================================================
    # Helpers
    # ==========================================================

    async def _run(
        self,
        tool: Tool,
        parameters: dict,
        context: ToolExecutionContext | None,
    ) -> ToolResult:

        if self.tracer is None:

            return await self._run_traced(
                tool,
                parameters,
                context,
                None,
            )

        with self.tracer.span(
            "tool.execute",
            {
                "tool": tool.name,
                "incident_id": (
                    context.incident_id if context else ""
                ),
            },
        ) as span:

            return await self._run_traced(
                tool,
                parameters,
                context,
                span,
            )

    async def _run_traced(
        self,
        tool: Tool,
        parameters: dict,
        context: ToolExecutionContext | None,
        span,
    ) -> ToolResult:

        try:

            result = await tool.execute(
                parameters,
                context,
            )

            if span is not None:

                span.set_attribute(
                    "success",
                    result.success,
                )

            return result

        except Exception as ex:

            if span is not None:
                span.record_error(ex)

            return ToolResult(
                tool=tool.name,
                success=False,
                error=str(ex),
            )

    @staticmethod
    def _context_to_dict(
        context: ToolExecutionContext | None,
    ) -> dict | None:

        if context is None:
            return None

        return {
            "incident_id": context.incident_id,
            "workflow_id": context.workflow_id,
            "actor": context.actor,
        }

    @staticmethod
    def _context_from_dict(
        data: dict | None,
    ) -> ToolExecutionContext | None:

        if not data:
            return None

        return ToolExecutionContext(
            incident_id=data.get("incident_id"),
            workflow_id=data.get("workflow_id"),
            actor=data.get("actor"),
        )
