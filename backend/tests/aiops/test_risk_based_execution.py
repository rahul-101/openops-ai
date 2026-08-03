import pytest

from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.governance.exceptions import (
    BlockedActionError,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


@pytest.fixture
def risk() -> RiskBasedExecutor:

    executor = RiskBasedExecutor()

    executor.register_action(
        "tool.kubernetes.pod_status",
        RiskLevel.LOW,
    )

    executor.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    executor.register_action(
        "tool.aws.delete",
        RiskLevel.HIGH,
    )

    return executor


def test_safe_action_auto_executes(risk):

    assert risk.can_auto_execute("tool.kubernetes.pod_status") is True


def test_medium_risk_requires_approval(risk):

    assert risk.can_auto_execute("tool.kubernetes.restart") is False


def test_high_risk_blocked(risk):

    assert risk.is_blocked("tool.aws.delete") is True


def test_evaluate_returns_plan(risk):

    plan = risk.evaluate("tool.kubernetes.restart")

    assert plan.action == "tool.kubernetes.restart"
    assert plan.risk_level == RiskLevel.MEDIUM
    assert plan.decision == ActionDecision.APPROVAL_REQUIRED
    assert plan.approved is False


def test_evaluate_low_risk_approved(risk):

    plan = risk.evaluate("tool.kubernetes.pod_status")

    assert plan.approved is True


def test_authorize_raises_for_high_risk(risk):

    with pytest.raises(BlockedActionError):
        risk.authorize("tool.aws.delete")


def test_authorize_passes_for_low_risk(risk):

    assert (
        risk.authorize("tool.kubernetes.pod_status")
        == ActionDecision.AUTO_EXECUTED
    )


def test_actions_mapping(risk):

    actions = risk.actions()

    assert actions["tool.kubernetes.pod_status"] == RiskLevel.LOW

    assert actions["tool.aws.delete"] == RiskLevel.HIGH
