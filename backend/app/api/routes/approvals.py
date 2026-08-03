from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.tools.approval import ApprovalWorkflow
from app.infrastructure.tools.exceptions import (
    ToolApprovalDeniedError,
)
from app.infrastructure.tools.executor import ToolExecutor
from app.infrastructure.dependencies import (
    get_approval_workflow,
    get_tool_executor,
)

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


def _serialize(
    approval,
) -> dict:

    data = asdict(approval)

    data["status"] = approval.status.value

    return data


@router.get(
    "/pending",
    summary="List pending approval requests",
)
def list_pending(
    workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    return [
        _serialize(approval)
        for approval in workflow.list_pending()
    ]


@router.get(
    "/history",
    summary="List all approval requests",
)
def history(
    limit: int | None = None,
    workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    items = workflow.history()

    if limit is not None:
        items = items[-limit:]

    return [
        _serialize(approval)
        for approval in items
    ]


@router.get(
    "/{approval_id}",
    summary="Get a single approval request",
)
def get_approval(
    approval_id: str,
    workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    approval = workflow.get(approval_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found.",
        )

    return _serialize(approval)


@router.post(
    "/{approval_id}/approve",
    summary="Approve a pending approval request",
)
def approve(
    approval_id: str,
    body: dict | None = None,
    workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    try:

        approval = workflow.approve(
            approval_id,
            approved_by=(
                (body or {}).get("approved_by")
                or "operator"
            ),
        )

    except ToolApprovalDeniedError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex),
        )

    return _serialize(approval)


@router.post(
    "/{approval_id}/reject",
    summary="Reject a pending approval request",
)
def reject(
    approval_id: str,
    body: dict | None = None,
    workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    try:

        approval = workflow.reject(
            approval_id,
            approved_by=(
                (body or {}).get("approved_by")
                or "operator"
            ),
            reason=(body or {}).get("reason"),
        )

    except ToolApprovalDeniedError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex),
        )

    return _serialize(approval)


@router.post(
    "/{approval_id}/execute",
    summary="Execute an approved approval request",
)
async def execute(
    approval_id: str,
    executor: ToolExecutor = Depends(
        get_tool_executor,
    ),
):

    try:

        result = await executor.execute_approved(
            approval_id,
        )

    except ToolApprovalDeniedError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex),
        )

    return {
        "success": result.success,
        "data": result.data,
        "error": result.error,
    }
