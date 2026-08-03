import pytest

from app.infrastructure.governance.approval_policy import (
    ApprovalPolicyEngine,
)
from app.infrastructure.governance.exceptions import (
    BlockedActionError,
)
from app.infrastructure.governance.models import (
    ActionDecision,
    RiskLevel,
)


@pytest.fixture
def engine() -> ApprovalPolicyEngine:

    service = ApprovalPolicyEngine()

    service.register_action(
        "incident.analyze",
        RiskLevel.LOW,
    )

    service.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    service.register_action(
        "tool.aws.delete",
        RiskLevel.HIGH,
    )

    return service


def test_default_risk_is_medium(engine):

    assert (
        engine.risk_level("unknown.action")
        == RiskLevel.MEDIUM
    )


def test_registered_risk_levels(engine):

    assert engine.risk_level("incident.analyze") == RiskLevel.LOW

    assert (
        engine.risk_level("tool.kubernetes.restart")
        == RiskLevel.MEDIUM
    )

    assert (
        engine.risk_level("tool.aws.delete")
        == RiskLevel.HIGH
    )


def test_low_risk_auto_executes(engine):

    assert (
        engine.evaluate("incident.analyze")
        == ActionDecision.AUTO_EXECUTED
    )


def test_medium_risk_requires_approval(engine):

    assert (
        engine.evaluate("tool.kubernetes.restart")
        == ActionDecision.APPROVAL_REQUIRED
    )


def test_high_risk_blocked(engine):

    assert (
        engine.evaluate("tool.aws.delete")
        == ActionDecision.BLOCKED
    )


def test_authorize_passes_for_low_risk(engine):

    assert (
        engine.authorize("incident.analyze")
        == ActionDecision.AUTO_EXECUTED
    )


def test_authorize_passes_for_medium_risk(engine):

    assert (
        engine.authorize("tool.kubernetes.restart")
        == ActionDecision.APPROVAL_REQUIRED
    )


def test_authorize_raises_for_high_risk(engine):

    with pytest.raises(BlockedActionError):
        engine.authorize("tool.aws.delete")


def test_actions_mapping(engine):

    actions = engine.actions()

    assert actions["incident.analyze"] == RiskLevel.LOW

    assert actions["tool.aws.delete"] == RiskLevel.HIGH
