from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.governance.models import RiskLevel


@dataclass(frozen=True)
class ReasoningFactor:
    """
    A single reasoning factor that influenced a decision.
    """

    label: str

    weight: float = 0.0


@dataclass
class DecisionConfidence:
    """
    The computed confidence and risk for a decision.
    """

    decision: str

    confidence: float

    risk: RiskLevel

    reasoning: list[str] = field(default_factory=list)

    factors: list[ReasoningFactor] = field(
        default_factory=list
    )

    validated: bool = False

    computed_at: datetime = field(
        default_factory=datetime.utcnow
    )

    @property
    def risk_classification(self) -> str:
        return self.risk.value


class DecisionConfidenceEngine:
    """
    Computes a confidence score, risk classification, and
    reasoning factors for a decision.
    """

    BASE_CONFIDENCE = 0.5

    FACTOR_STEP = 0.12

    MAX_CONFIDENCE = 0.98

    VALIDATION_THRESHOLD = 0.8

    def evaluate(
        self,
        *,
        decision: str,
        factors: list[str],
        severity: str = "low",
        verified: bool = False,
    ) -> DecisionConfidence:
        """
        Evaluates the decision and returns a confidence,
        risk classification, and reasoning summary.
        """

        parsed = self._parse_factors(factors)

        confidence = self._score(parsed)

        risk = self._classify_risk(
            confidence,
            severity,
            verified,
        )

        validated = self._validate(
            confidence,
            risk,
            verified,
        )

        reasoning = self._reasoning(
            parsed,
            risk,
            verified,
        )

        return DecisionConfidence(
            decision=decision,
            confidence=confidence,
            risk=risk,
            reasoning=reasoning,
            factors=parsed,
            validated=validated,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def _parse_factors(
        self,
        factors: list[str],
    ) -> list[ReasoningFactor]:

        return [
            ReasoningFactor(
                label=factor,
                weight=self._factor_weight(factor),
            )
            for factor in factors
        ]

    def _factor_weight(
        self,
        factor: str,
    ) -> float:

        text = factor.lower()

        strong = (
            "timeout",
            "crash",
            "error rate",
            "resource",
            "recovery",
            "verified",
            "resolved previously",
        )

        if any(word in text for word in strong):
            return 1.0

        if "possible" in text or "potential" in text:
            return 0.3

        return 0.5

    def _score(
        self,
        factors: list[ReasoningFactor],
    ) -> float:

        if not factors:
            return self.BASE_CONFIDENCE

        weighted = sum(
            factor.weight for factor in factors
        )

        score = self.BASE_CONFIDENCE + (
            min(weighted, 4.0) * self.FACTOR_STEP
        )

        return min(score, self.MAX_CONFIDENCE)

    def _classify_risk(
        self,
        confidence: float,
        severity: str,
        verified: bool,
    ) -> RiskLevel:

        high_severity = severity.lower() in (
            "high",
            "critical",
            "sev1",
            "p1",
        )

        if high_severity and not verified:
            return RiskLevel.HIGH

        if high_severity and confidence < 0.8:
            return RiskLevel.MEDIUM

        if not verified and confidence < 0.6:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _validate(
        self,
        confidence: float,
        risk: RiskLevel,
        verified: bool,
    ) -> bool:

        if risk == RiskLevel.HIGH:
            return False

        if not verified and risk == RiskLevel.MEDIUM:
            return False

        return confidence >= self.VALIDATION_THRESHOLD

    def _reasoning(
        self,
        factors: list[ReasoningFactor],
        risk: RiskLevel,
        verified: bool,
    ) -> list[str]:

        reasoning = [
            factor.label for factor in factors
        ]

        reasoning.append(
            f"risk classified as {risk.value}"
        )

        if verified:
            reasoning.append(
                "recommendation verified before execution"
            )
        else:
            reasoning.append(
                "verification pending for final action"
            )

        return reasoning
