from app.infrastructure.reasoning.confidence import (
    DecisionConfidenceEngine,
)
from app.infrastructure.governance.models import RiskLevel


def test_low_risk_high_confidence_validated():

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="restart_service",
        factors=[
            "high API error rate",
            "database timeout detected",
            "similar incident resolved previously",
        ],
        severity="low",
        verified=True,
    )

    assert confidence.confidence > 0.8
    assert confidence.risk == RiskLevel.LOW
    assert confidence.validated is True


def test_high_severity_unverified_is_high_risk():

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="restart_service",
        factors=[
            "high API error rate",
            "database timeout detected",
        ],
        severity="high",
        verified=False,
    )

    assert confidence.risk == RiskLevel.HIGH
    assert confidence.validated is False


def test_no_factors_base_confidence():

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="monitor_only",
        factors=[],
        severity="low",
        verified=True,
    )

    assert confidence.confidence == engine.BASE_CONFIDENCE


def test_reasoning_includes_factors_and_risk():

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="restart_service",
        factors=["database timeout detected"],
        severity="low",
        verified=True,
    )

    assert "database timeout detected" in confidence.reasoning
    assert any(
        "risk classified" in factor
        for factor in confidence.reasoning
    )


def test_confidence_clamped_at_max():

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="restart_service",
        factors=[
            "high API error rate",
            "database timeout detected",
            "service crash loop detected",
            "resource exhaustion detected",
            "high severity incident",
        ],
        severity="low",
        verified=True,
    )

    assert confidence.confidence <= engine.MAX_CONFIDENCE
