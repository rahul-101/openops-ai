from threading import Lock

from app.infrastructure.governance.exceptions import (
    BlockedActionError,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


class ApprovalPolicyEngine:
    """
    Governs action execution by risk level.

    Rules:
    - low risk    -> auto execute
    - medium risk -> approval required
    - high risk   -> block
    """

    DEFAULT_RISK = RiskLevel.MEDIUM

    def __init__(self) -> None:

        self._actions: dict[str, RiskLevel] = {}

        self._lock = Lock()

    def register_action(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> None:

        with self._lock:
            self._actions[action.lower()] = risk_level

    def risk_level(
        self,
        action: str,
    ) -> RiskLevel:

        with self._lock:
            return self._actions.get(
                action.lower(),
                self.DEFAULT_RISK,
            )

    def evaluate(
        self,
        action: str,
    ) -> ActionDecision:

        risk = self.risk_level(action)

        if risk == RiskLevel.LOW:
            return ActionDecision.AUTO_EXECUTED

        if risk == RiskLevel.MEDIUM:
            return ActionDecision.APPROVAL_REQUIRED

        return ActionDecision.BLOCKED

    def authorize(
        self,
        action: str,
    ) -> ActionDecision:
        """
        Raises BlockedActionError for high risk actions.
        """

        decision = self.evaluate(action)

        if decision == ActionDecision.BLOCKED:
            raise BlockedActionError(
                f"Action '{action}' is blocked by policy."
            )

        return decision

    def actions(self) -> dict[str, RiskLevel]:

        with self._lock:
            return dict(self._actions)
