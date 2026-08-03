import pytest

from app.infrastructure.tools.approval import ApprovalWorkflow
from app.infrastructure.tools.base import Tool
from app.infrastructure.tools.exceptions import (
    ToolApprovalDeniedError,
    ToolApprovalRequiredError,
)
from app.infrastructure.tools.executor import ToolExecutor
from app.infrastructure.tools.models import (
    ApprovalStatus,
    ToolCategory,
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)
from app.infrastructure.tools.registry import ToolRegistry


class RiskyTool(Tool):

    RISKY_ACTIONS = ("delete",)

    def __init__(self):
        super().__init__(
            ToolMetadata(
                name="risky",
                category=ToolCategory.DATABASE,
                description="risky test tool",
            )
        )

    async def execute(self, parameters, context=None) -> ToolResult:
        return ToolResult(
            tool=self.name,
            success=True,
            data={"deleted": parameters.get("name")},
        )


@pytest.fixture
def setup():

    registry = ToolRegistry()
    registry.register(RiskyTool())

    approval = ApprovalWorkflow()

    executor = ToolExecutor(
        registry=registry,
        approval=approval,
    )

    return registry, approval, executor


@pytest.mark.asyncio
async def test_safe_action_executes_directly(setup):

    _, _, executor = setup

    result = await executor.execute(
        "risky",
        {"action": "read"},
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_risky_action_requires_approval(setup):

    _, _, executor = setup

    result = await executor.execute(
        "risky",
        {"action": "delete", "name": "prod-db"},
    )

    assert result.success is False
    assert "approval_id" in result.data
    assert result.data["status"] == "pending"


@pytest.mark.asyncio
async def test_execute_without_approval_workflow_raises():

    registry = ToolRegistry()
    registry.register(RiskyTool())

    executor = ToolExecutor(registry)

    with pytest.raises(ToolApprovalRequiredError):
        await executor.execute(
            "risky",
            {"action": "delete"},
        )


@pytest.mark.asyncio
async def test_execute_approved_after_approval(setup):

    _, approval, executor = setup

    pending = await executor.execute(
        "risky",
        {"action": "delete", "name": "prod-db"},
    )

    approval_id = pending.data["approval_id"]

    approval.approve(approval_id, approved_by="admin")

    result = await executor.execute_approved(approval_id)

    assert result.success is True
    assert result.data["deleted"] == "prod-db"

    executed = approval.get(approval_id)

    assert executed.status == ApprovalStatus.EXECUTED
    assert executed.result == result.data


@pytest.mark.asyncio
async def test_execute_approved_rejected_raises(setup):

    _, approval, executor = setup

    pending = await executor.execute(
        "risky",
        {"action": "delete", "name": "prod-db"},
    )

    approval_id = pending.data["approval_id"]

    approval.reject(approval_id, reason="no")

    with pytest.raises(ToolApprovalDeniedError):
        await executor.execute_approved(approval_id)


@pytest.mark.asyncio
async def test_approval_history(setup):

    _, approval, executor = setup

    await executor.execute(
        "risky",
        {"action": "delete", "name": "db-1"},
    )

    await executor.execute(
        "risky",
        {"action": "delete", "name": "db-2"},
    )

    history = approval.history()

    assert len(history) == 2
    assert len(approval.list_pending()) == 2

    approval.approve(history[0].id)

    assert len(approval.list_pending()) == 1


@pytest.mark.asyncio
async def test_executor_passes_context():

    registry = ToolRegistry()
    registry.register(RiskyTool())

    approval = ApprovalWorkflow()

    executor = ToolExecutor(registry, approval)

    pending = await executor.execute(
        "risky",
        {"action": "delete", "name": "db-1"},
        context=ToolExecutionContext(
            incident_id="inc-1",
            actor="bot",
        ),
    )

    approval_id = pending.data["approval_id"]

    approval.approve(approval_id)

    await executor.execute_approved(approval_id)

    request = approval.get(approval_id)

    assert request.context["incident_id"] == "inc-1"
    assert request.context["actor"] == "bot"
