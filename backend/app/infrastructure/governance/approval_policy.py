from threading import Lock
from typing import Optional

from app.core.config import settings
from app.infrastructure.governance.exceptions import (
    BlockedActionError,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)
from app.infrastructure.persistence.mongodb import get_database


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

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.governance.mongo_approval_repository import (
                MongoApprovalRepository,
            )
            self._mongo_repo = MongoApprovalRepository()
            # Load from MongoDB
            loaded = self._mongo_repo.get_all_actions()
            self._actions.update(loaded)

    def register_action(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> None:

        with self._lock:
            self._actions[action.lower()] = risk_level

        if self._mongo_repo is not None:
            self._mongo_repo.save_action(action, risk_level)

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

    def clear(self) -> None:

        with self._lock:
            self._actions.clear()

        if self._mongo_repo is not None:
            self._mongo_repo.clear()

    def actions(self) -> dict[str, RiskLevel]:

        with self._lock:
            return dict(self._actions)
