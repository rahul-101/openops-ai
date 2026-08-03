from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DecisionExplanation:
    """
    Human readable explanation of an autonomous decision.
    """

    decision: str

    why: str

    evidence: list[str] = field(default_factory=list)

    alternatives: list[str] = field(default_factory=list)

    confidence: float = 0.0

    risk: str = "low"

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class DecisionExplainer:
    """
    Produces a human readable explanation for a decision,
    covering why it was made, the evidence used, and the
    alternative actions that were considered.
    """

    def explain(
        self,
        *,
        decision: str,
        why: str,
        evidence: list[str] | None = None,
        alternatives: list[str] | None = None,
        confidence: float = 0.0,
        risk: str = "low",
    ) -> DecisionExplanation:

        if alternatives is None:
            alternatives = self._default_alternatives(risk)

        return DecisionExplanation(
            decision=decision,
            why=why,
            evidence=list(evidence or []),
            alternatives=list(alternatives),
            confidence=confidence,
            risk=risk,
        )

    def explain_confidence(
        self,
        confidence,
    ) -> DecisionExplanation:
        """
        Builds an explanation directly from a decision
        confidence record.
        """

        reasoning = confidence.reasoning

        return DecisionExplanation(
            decision=confidence.decision,
            why=self._why(confidence),
            evidence=[
                factor for factor in reasoning
                if not factor.startswith("risk classified")
            ],
            alternatives=self._alternatives(confidence),
            confidence=confidence.confidence,
            risk=confidence.risk.value,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _default_alternatives(risk: str) -> list[str]:

        if risk == "low":
            return ["monitor only"]

        if risk == "medium":
            return [
                "escalate for manual approval",
                "monitor only",
            ]

        return [
            "escalate for manual investigation",
            "monitor only",
        ]

    @staticmethod
    def _why(confidence) -> str:

        if not confidence.factors:
            return (
                "No strong evidence was available; "
                "decision made conservatively."
            )

        top = confidence.reasoning[:2]

        return (
            "Decision made because "
            + ", ".join(top)
            + "."
        )

    @staticmethod
    def _alternatives(confidence) -> list[str]:

        if confidence.risk.value == "low":
            return ["monitor only"]

        if confidence.risk.value == "medium":
            return [
                "escalate for manual approval",
                "monitor only",
            ]

        return [
            "escalate for manual investigation",
            "monitor only",
        ]
