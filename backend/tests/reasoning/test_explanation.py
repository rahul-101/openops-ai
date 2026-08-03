from app.infrastructure.reasoning.explanation import (
    DecisionExplainer,
)
from app.infrastructure.reasoning.confidence import (
    DecisionConfidenceEngine,
)


def test_explain_captures_why_evidence_alternatives():

    explainer = DecisionExplainer()

    explanation = explainer.explain(
        decision="restart_service",
        why="high error rate and database timeout",
        evidence=["error rate 45%", "db timeout"],
        alternatives=["monitor only", "scale up"],
        confidence=0.94,
        risk="low",
    )

    assert explanation.decision == "restart_service"
    assert "error rate" in explanation.why
    assert len(explanation.evidence) == 2
    assert len(explanation.alternatives) == 2
    assert explanation.confidence == 0.94


def test_explain_confidence_builds_from_record():

    explainer = DecisionExplainer()

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="restart_service",
        factors=["database timeout detected"],
        severity="low",
        verified=True,
    )

    explanation = explainer.explain_confidence(confidence)

    assert explanation.decision == "restart_service"
    assert explanation.risk == confidence.risk.value
    assert explanation.confidence == confidence.confidence
    assert len(explanation.evidence) >= 1


def test_explain_confidence_no_reasoning_conservative():

    explainer = DecisionExplainer()

    engine = DecisionConfidenceEngine()

    confidence = engine.evaluate(
        decision="monitor_only",
        factors=[],
        severity="low",
        verified=True,
    )

    explanation = explainer.explain_confidence(confidence)

    assert "No strong evidence" in explanation.why


def test_alternatives_depend_on_risk():

    explainer = DecisionExplainer()

    low = explainer.explain(
        decision="d",
        why="w",
        risk="low",
    )

    high = explainer.explain(
        decision="d",
        why="w",
        risk="high",
    )

    assert "monitor only" in low.alternatives
    assert "manual investigation" in high.alternatives[0]
