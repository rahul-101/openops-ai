from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
    VerificationStatus,
)


def test_low_risk_high_confidence_approved():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="restart deployment",
        confidence=0.94,
        risk="low",
    )

    assert result.status == VerificationStatus.APPROVED
    assert result.approved is True
    assert "recommendation_present" in result.checks
    assert "confidence_ok" in result.checks


def test_high_risk_rejected():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="delete production database",
        confidence=0.95,
        risk="high",
    )

    assert result.status == VerificationStatus.REJECTED
    assert result.approved is False


def test_medium_risk_requires_review():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="restart deployment",
        confidence=0.94,
        risk="medium",
    )

    assert (
        result.status
        == VerificationStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="restart deployment",
        confidence=0.3,
        risk="low",
    )

    assert (
        result.status
        == VerificationStatus.REVIEW_REQUIRED
    )


def test_missing_recommendation_rejected():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="",
        confidence=0.94,
        risk="low",
    )

    assert result.status == VerificationStatus.REJECTED
    assert "recommendation_missing" in result.checks


def test_approve_after_review():

    verification = SelfVerificationLayer()

    result = verification.validate(
        recommendation="restart deployment",
        confidence=0.3,
        risk="low",
    )

    approved = verification.approve_after_review(result)

    assert approved.status == VerificationStatus.APPROVED


def test_custom_confidence_threshold():

    verification = SelfVerificationLayer(min_confidence=0.5)

    result = verification.validate(
        recommendation="restart deployment",
        confidence=0.6,
        risk="low",
    )

    assert result.status == VerificationStatus.APPROVED
