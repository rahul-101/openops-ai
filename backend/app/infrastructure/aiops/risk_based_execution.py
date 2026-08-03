from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from app.infrastructure.governance.approval_policy import (
    ApprovalPolicyEngine,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


@dataclass
class ExecutionPlan:
    """
    Result of evaluating an action against the risk policy.
    """

    action: str

    risk_level: RiskLevel

    decision: ActionDecision

    approved: bool = False

    evaluated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class RiskBasedExecutor:
    """
    Decides whether an action can execute based on risk.

    - Safe (low risk) actions auto execute.
    - Medium risk actions require approval.
    - Unsafe (high risk) actions are blocked.
    """

    def __init__(
        self,
        policy: ApprovalPolicyEngine | None = None,
    ) -> None:

        self._policy = (
            policy or ApprovalPolicyEngine()
        )

        self._lock = Lock()

    def register_action(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> None:

        self._policy.register_action(
            action,
            risk_level,
        )

    def risk_level(
        self,
        action: str,
    ) -> RiskLevel:

        return self._policy.risk_level(action)

    def evaluate(
        self,
        action: str,
    ) -> ExecutionPlan:

        decision = self._policy.evaluate(action)

        return ExecutionPlan(
            action=action,
            risk_level=self.risk_level(action),
            decision=decision,
            approved=(
                decision == ActionDecision.AUTO_EXECUTED
            ),
        )

    def can_auto_execute(
        self,
        action: str,
    ) -> bool:
        """
        True when a safe action can execute without approval.
        """

        return (
            self._policy.evaluate(action)
            == ActionDecision.AUTO_EXECUTED
        )

    def is_blocked(
        self,
        action: str,
    ) -> bool:

        return (
            self._policy.evaluate(action)
            == ActionDecision.BLOCKED
        )

    def authorize(
        self,
        action: str,
    ) -> ActionDecision:
        """
        Raises BlockedActionError for high risk actions.
        """

        return self._policy.authorize(action)

    def actions(self) -> dict[str, RiskLevel]:

        return self._policy.actions()
