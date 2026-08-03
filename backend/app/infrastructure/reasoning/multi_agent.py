from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
    IncidentAnalysis,
)
from app.infrastructure.aiops.event_ingestion import (
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import Playbook
from app.infrastructure.reasoning.confidence import (
    DecisionConfidence,
    DecisionConfidenceEngine,
)
from app.infrastructure.reasoning.explanation import (
    DecisionExplainer,
)
from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
    VerificationResult,
)


class ReasoningAgentStatus(str, Enum):
    """
    Execution outcome of a reasoning agent.
    """

    SUCCESS = "success"

    FAILURE = "failure"

    SKIPPED = "skipped"


@dataclass
class ReasoningAgentResult:
    """
    Result produced by a single reasoning agent.
    """

    agent: str

    status: ReasoningAgentStatus

    output: dict = field(default_factory=dict)

    error: str | None = None

    executed_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class ReasoningContext:
    """
    Shared state passed through the multi-agent reasoning flow.
    """

    event: NormalizedEvent

    analysis: IncidentAnalysis | None = None

    decision: str | None = None

    playbook: Playbook | None = None

    reasoning_factors: list[str] = field(
        default_factory=list
    )

    evidence: list[str] = field(default_factory=list)

    alternatives: list[str] = field(default_factory=list)

    verification: VerificationResult | None = None

    confidence: DecisionConfidence | None = None

    explanation: dict = field(default_factory=dict)

    history_id: str | None = None


class ReasoningAgent(ABC):
    """
    Contract for every reasoning agent.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    async def execute(
        self,
        context: ReasoningContext,
    ) -> ReasoningAgentResult:
        raise NotImplementedError


class IncidentAnalysisAgent(ReasoningAgent):
    """
    Analyzes the incident event and derives the initial
    reasoning factors and evidence.
    """

    def __init__(
        self,
        engine: AutonomousDecisionEngine,
    ) -> None:

        super().__init__("incident_analysis")

        self.engine = engine

    async def execute(
        self,
        context: ReasoningContext,
    ) -> ReasoningAgentResult:

        analysis = self.engine.analyze(context.event)

        context.analysis = analysis

        context.reasoning_factors = self._factors(
            context.event,
            analysis,
        )

        context.evidence = self._evidence(
            context.event,
            analysis,
        )

        return ReasoningAgentResult(
            agent=self.name,
            status=ReasoningAgentStatus.SUCCESS,
            output={
                "incident_id": context.event.event_id,
                "summary": analysis.summary,
                "category": analysis.category,
                "probable_cause": analysis.probable_cause,
                "recommendation": analysis.recommendation,
                "factors": list(context.reasoning_factors),
                "evidence": list(context.evidence),
            },
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _factors(
        event: NormalizedEvent,
        analysis: IncidentAnalysis,
    ) -> list[str]:

        description = (
            event.description or event.title
        ).lower()

        factors: list[str] = []

        if any(
            word in description
            for word in ("error", "failure", "exception")
        ):
            factors.append("high API error rate")

        if any(
            word in description
            for word in ("database", "timeout", "db")
        ):
            factors.append("database timeout detected")

        if any(
            word in description
            for word in ("crash", "restart", "loop")
        ):
            factors.append("service crash loop detected")

        if any(
            word in description
            for word in ("cpu", "memory", "disk")
        ):
            factors.append("resource exhaustion detected")

        if event.severity.value in (
            "high",
            "critical",
        ):
            factors.append("high severity incident")

        if analysis.confidence >= 0.7:
            factors.append(
                "known root cause signature matched"
            )

        return factors

    @staticmethod
    def _evidence(
        event: NormalizedEvent,
        analysis: IncidentAnalysis,
    ) -> list[str]:

        evidence = [
            f"source: {event.source}",
            f"severity: {event.severity.value}",
        ]

        if event.tags:
            evidence.append(
                f"tags: {', '.join(event.tags)}"
            )

        evidence.append(
            f"root cause analysis: {analysis.probable_cause}"
        )

        return evidence


class RcaAgent(ReasoningAgent):
    """
    Deepens the root cause analysis and appends the
    probable cause as a reasoning factor.
    """

    def __init__(self) -> None:

        super().__init__("rca")

    async def execute(
        self,
        context: ReasoningContext,
    ) -> ReasoningAgentResult:

        analysis = context.analysis

        if analysis is None:
            return ReasoningAgentResult(
                agent=self.name,
                status=ReasoningAgentStatus.FAILURE,
                error="No incident analysis available.",
            )

        if analysis.probable_cause:
            factor = (
                "root cause identified: "
                f"{analysis.probable_cause}"
            )

            if factor not in context.reasoning_factors:
                context.reasoning_factors.append(factor)

        context.alternatives = self._alternatives(analysis)

        return ReasoningAgentResult(
            agent=self.name,
            status=ReasoningAgentStatus.SUCCESS,
            output={
                "probable_cause": analysis.probable_cause,
                "category": analysis.category,
                "recommendation": analysis.recommendation,
                "alternatives": list(context.alternatives),
            },
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _alternatives(
        analysis: IncidentAnalysis,
    ) -> list[str]:

        recommendation = analysis.recommendation.lower()

        alternatives = ["monitor and observe"]

        if "restart" in recommendation:
            alternatives.append("scale up deployment")

        if "scale" in recommendation:
            alternatives.append("restart affected pod")

        if "investigate" in recommendation:
            alternatives.append("apply last known good config")

        alternatives.append("escalate for manual investigation")

        return alternatives


class VerificationAgent(ReasoningAgent):
    """
    Validates the recommendation before the final decision.
    """

    def __init__(
        self,
        verification: SelfVerificationLayer,
    ) -> None:

        super().__init__("verification")

        self.verification = verification

    async def execute(
        self,
        context: ReasoningContext,
    ) -> ReasoningAgentResult:

        analysis = context.analysis

        recommendation = (
            analysis.recommendation
            if analysis is not None
            else ""
        )

        confidence = (
            analysis.confidence if analysis is not None else 0.0
        )

        result = self.verification.validate(
            recommendation=recommendation,
            confidence=confidence,
            risk=context.event.severity.value,
        )

        context.verification = result

        return ReasoningAgentResult(
            agent=self.name,
            status=ReasoningAgentStatus.SUCCESS,
            output={
                "status": result.status.value,
                "reason": result.reason,
                "checks": list(result.checks),
            },
        )


class DecisionAgent(ReasoningAgent):
    """
    Produces the final decision with a confidence score, risk
    classification, and reasoning factors.
    """

    def __init__(
        self,
        confidence_engine: DecisionConfidenceEngine,
        explainer: DecisionExplainer,
    ) -> None:

        super().__init__("decision")

        self.confidence_engine = confidence_engine

        self.explainer = explainer

    async def execute(
        self,
        context: ReasoningContext,
    ) -> ReasoningAgentResult:

        analysis = context.analysis

        decision = self._decision(analysis)

        context.decision = decision

        verified = (
            context.verification is not None
            and context.verification.approved
        )

        confidence = self.confidence_engine.evaluate(
            decision=decision,
            factors=list(context.reasoning_factors),
            severity=context.event.severity.value,
            verified=verified,
        )

        context.confidence = confidence

        explanation = self.explainer.explain_confidence(
            confidence
        )

        context.explanation = {
            "why": explanation.why,
            "evidence": list(explanation.evidence),
            "alternatives": list(
                explanation.alternatives
            ),
        }

        return ReasoningAgentResult(
            agent=self.name,
            status=ReasoningAgentStatus.SUCCESS,
            output={
                "decision": decision,
                "confidence": round(confidence.confidence, 4),
                "risk": confidence.risk.value,
                "validated": confidence.validated,
                "reasoning": list(confidence.reasoning),
                "explanation": dict(context.explanation),
            },
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _decision(
        analysis: IncidentAnalysis | None,
    ) -> str:

        if analysis is None:
            return "escalate_incident"

        recommendation = analysis.recommendation.lower()

        if "restart" in recommendation:
            return "restart_service"

        if "scale" in recommendation:
            return "scale_service"

        if "investigate" in recommendation:
            return "investigate_dependencies"

        if "escalate" in recommendation:
            return "escalate_incident"

        return "monitor_only"


class MultiAgentReasoningRunner:
    """
    Runs the reasoning agents in a fixed order sharing context.
    """

    def __init__(
        self,
        agents: list[ReasoningAgent],
    ) -> None:

        self.agents = agents

    async def run(
        self,
        context: ReasoningContext,
    ) -> list[ReasoningAgentResult]:

        results: list[ReasoningAgentResult] = []

        for agent in self.agents:

            result = await agent.execute(context)

            results.append(result)

        return results
