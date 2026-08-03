from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VerificationStatus(str, Enum):
    """
    Outcome of validating a recommendation before execution.
    """

    APPROVED = "approved"

    REJECTED = "rejected"

    REVIEW_REQUIRED = "review_required"


@dataclass
class VerificationResult:
    """
    Result of validating a recommendation before execution.
    """

    status: VerificationStatus

    reason: str = ""

    checks: list[str] = field(default_factory=list)

    validated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    @property
    def approved(self) -> bool:
        return self.status == VerificationStatus.APPROVED


class SelfVerificationLayer:
    """
    Validates a recommendation before execution.

    - Checks that a recommendation is present.
    - Checks the confidence against a threshold.
    - Checks the risk classification.
    - Approves / rejects / requests review accordingly.
    """

    MIN_CONFIDENCE = 0.7

    HIGH_RISK_VALUES = ("high",)

    REVIEW_RISK_VALUES = ("medium",)

    def __init__(
        self,
        min_confidence: float = MIN_CONFIDENCE,
    ) -> None:

        self.min_confidence = min_confidence

    def validate(
        self,
        *,
        recommendation: str,
        confidence: float = 0.0,
        risk: str = "low",
    ) -> VerificationResult:

        checks: list[str] = []

        # =====================================================
        # 1. Recommendation present
        # =====================================================

        if not recommendation.strip():
            return VerificationResult(
                status=VerificationStatus.REJECTED,
                reason="No recommendation provided to validate.",
                checks=["recommendation_missing"],
            )

        checks.append("recommendation_present")

        # =====================================================
        # 2. Confidence threshold
        # =====================================================

        if confidence >= self.min_confidence:
            checks.append("confidence_ok")
        else:
            checks.append("confidence_low")

        # =====================================================
        # 3. Risk classification
        # =====================================================

        checks.append(f"risk_{risk}")

        if risk.lower() in self.HIGH_RISK_VALUES:
            return VerificationResult(
                status=VerificationStatus.REJECTED,
                reason=(
                    "High risk action rejected before execution."
                ),
                checks=checks,
            )

        if risk.lower() in self.REVIEW_RISK_VALUES:
            return VerificationResult(
                status=VerificationStatus.REVIEW_REQUIRED,
                reason=(
                    "Medium risk action requires review before "
                    "execution."
                ),
                checks=checks,
            )

        if confidence < self.min_confidence:
            return VerificationResult(
                status=VerificationStatus.REVIEW_REQUIRED,
                reason=(
                    "Low confidence requires review before "
                    "execution."
                ),
                checks=checks,
            )

        return VerificationResult(
            status=VerificationStatus.APPROVED,
            reason="Recommendation validated and approved.",
            checks=checks,
        )

    def approve(
        self,
        *,
        recommendation: str,
        confidence: float = 0.0,
        risk: str = "low",
    ) -> VerificationResult:

        return self.validate(
            recommendation=recommendation,
            confidence=confidence,
            risk=risk,
        )

    def approve_after_review(
        self,
        result: VerificationResult,
    ) -> VerificationResult:

        if (
            result.status
            == VerificationStatus.REVIEW_REQUIRED
        ):
            return VerificationResult(
                status=VerificationStatus.APPROVED,
                reason="Approved after manual review.",
                checks=result.checks,
            )

        return result
