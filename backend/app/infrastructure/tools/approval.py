from datetime import datetime
from threading import Lock

from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)
from app.infrastructure.tools.exceptions import (
    ToolApprovalDeniedError,
)
from app.infrastructure.tools.models import (
    ApprovalRequest,
    ApprovalStatus,
)


class ApprovalWorkflow:
    """
    Manages approval requests for risky tool actions.

    Records every request in an execution history for
    auditability.
    """

    def __init__(self) -> None:

        self._requests: dict[str, ApprovalRequest] = {}

        self._lock = Lock()

        self._store = new_store("approvals")

        if self._store is not None:

            for record in self._store.all():

                approval = from_jsonable(
                    record,
                    ApprovalRequest,
                )

                if approval is not None:
                    self._requests[approval.id] = approval

    def _persist(
        self,
        approval: ApprovalRequest,
    ) -> None:

        if self._store is not None:
            self._store.save(
                approval.id,
                to_jsonable(approval),
            )

    # ==========================================================
    # Request Lifecycle
    # ==========================================================

    def request(
        self,
        tool_name: str,
        parameters: dict,
        context: dict | None = None,
        requested_by: str | None = None,
    ) -> ApprovalRequest:

        approval = ApprovalRequest(
            tool_name=tool_name,
            parameters=dict(parameters),
            context=dict(context) if context else {},
            requested_by=requested_by,
        )

        with self._lock:
            self._requests[approval.id] = approval

        self._persist(approval)

        return approval

    def get(
        self,
        approval_id: str,
    ) -> ApprovalRequest | None:

        return self._requests.get(approval_id)

    # ==========================================================
    # Decision
    # ==========================================================

    def approve(
        self,
        approval_id: str,
        approved_by: str | None = None,
    ) -> ApprovalRequest:

        approval = self._get_required(approval_id)

        if approval.status != ApprovalStatus.PENDING:
            raise ToolApprovalDeniedError(
                f"Approval '{approval_id}' is not pending."
            )

        approval.status = ApprovalStatus.APPROVED
        approval.approved_by = approved_by
        approval.updated_at = datetime.utcnow()

        self._persist(approval)

        return approval

    def reject(
        self,
        approval_id: str,
        approved_by: str | None = None,
        reason: str | None = None,
    ) -> ApprovalRequest:

        approval = self._get_required(approval_id)

        approval.status = ApprovalStatus.REJECTED
        approval.approved_by = approved_by
        approval.reason = reason
        approval.updated_at = datetime.utcnow()

        self._persist(approval)

        return approval

    def mark_executed(
        self,
        approval_id: str,
        result: dict,
    ) -> ApprovalRequest:

        approval = self._get_required(approval_id)

        approval.status = ApprovalStatus.EXECUTED
        approval.result = result
        approval.updated_at = datetime.utcnow()

        self._persist(approval)

        return approval

    # ==========================================================
    # Queries
    # ==========================================================

    def list_pending(self) -> list[ApprovalRequest]:

        return [
            approval
            for approval in self._requests.values()
            if approval.status == ApprovalStatus.PENDING
        ]

    def history(self) -> list[ApprovalRequest]:

        with self._lock:
            return list(self._requests.values())

    def clear(self) -> None:

        with self._lock:
            self._requests.clear()

        if self._store is not None:
            self._store.clear()

    # ==========================================================
    # Helpers
    # ==========================================================

    def _get_required(
        self,
        approval_id: str,
    ) -> ApprovalRequest:

        approval = self._requests.get(approval_id)

        if approval is None:
            raise ToolApprovalDeniedError(
                f"Approval '{approval_id}' not found."
            )

        return approval
