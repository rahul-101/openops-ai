from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.aiops.event_ingestion import (
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import Playbook
from app.infrastructure.reasoning.history import (
    ReasoningHistoryRecord,
    ReasoningHistoryStore,
)
from app.infrastructure.reasoning.multi_agent import (
    MultiAgentReasoningRunner,
    ReasoningContext,
)


@dataclass
class ReasoningReport:
    """
    The full output of the multi-agent reasoning flow.
    """

    incident_id: str

    decision: str

    confidence: float

    risk: str

    reasoning: list[str] = field(default_factory=list)

    evidence: list[str] = field(default_factory=list)

    alternatives: list[str] = field(default_factory=list)

    explanation: dict = field(default_factory=dict)

    validated: bool = False

    agents_involved: list[str] = field(
        default_factory=list
    )

    model_selection: dict = field(default_factory=dict)

    history_id: str | None = None

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class ReasoningOrchestrator:
    """
    Runs the multi-agent reasoning flow for an incident and
    persists the reasoning history.
    """

    def __init__(
        self,
        runner: MultiAgentReasoningRunner,
        history: ReasoningHistoryStore,
        model_selector=None,
        publisher=None,
    ) -> None:

        self.runner = runner

        self.history = history

        self.model_selector = model_selector

        self.publisher = publisher

    async def reason(
        self,
        event: NormalizedEvent,
        playbook: Playbook | None = None,
    ) -> ReasoningReport:

        self._emit(
            "analysis_started",
            event,
            agent="reasoning",
            action="analyze",
        )

        context = ReasoningContext(
            event=event,
            playbook=playbook,
        )

        results = await self.runner.run(context)

        self._emit(
            "rca_completed",
            event,
            agent="reasoning",
            action="rca",
            status="success",
        )

        decision = context.decision or "escalate_incident"

        confidence = context.confidence

        explanation = context.explanation

        model_selection = self._select_model(event)

        agents_involved = [
            result.agent for result in results
        ]

        self._emit(
            "decision_created",
            event,
            agent="reasoning",
            action=decision,
            status=(
                "success"
                if confidence is not None
                and confidence.validated
                else "pending"
            ),
            metadata={
                "confidence": (
                    confidence.confidence
                    if confidence is not None
                    else 0.0
                ),
                "risk": (
                    confidence.risk.value
                    if confidence is not None
                    else "low"
                ),
                "model": (
                    model_selection.get("model")
                    if model_selection
                    else None
                ),
            },
        )

        record = self.history.record(
            incident_id=event.event_id,
            agents_involved=agents_involved,
            decisions=[decision],
            confidence=(
                round(confidence.confidence, 4)
                if confidence is not None
                else 0.0
            ),
            risk=(
                confidence.risk.value
                if confidence is not None
                else "low"
            ),
            outcome=(
                "approved"
                if (
                    confidence is not None
                    and confidence.validated
                )
                else "pending_review"
            ),
            explanation=explanation,
        )

        return ReasoningReport(
            incident_id=event.event_id,
            decision=decision,
            confidence=(
                round(confidence.confidence, 4)
                if confidence is not None
                else 0.0
            ),
            risk=(
                confidence.risk.value
                if confidence is not None
                else "low"
            ),
            reasoning=(
                list(confidence.reasoning)
                if confidence is not None
                else []
            ),
            evidence=list(context.evidence),
            alternatives=list(context.alternatives),
            explanation=dict(explanation),
            validated=(
                confidence.validated
                if confidence is not None
                else False
            ),
            agents_involved=agents_involved,
            model_selection=model_selection,
            history_id=record.incident_id,
        )

    def _select_model(
        self,
        event: NormalizedEvent,
    ) -> dict:

        if self.model_selector is None:
            return {}

        selection = self.model_selector.select(
            event.description or event.title,
            severity=event.severity.value,
            tags=event.tags,
        )

        if selection is None:
            return {}

        return {
            "model": selection.model,
            "provider": selection.provider,
            "complexity": selection.complexity.value,
            "reason": selection.reason,
        }

    def get_history(
        self,
        incident_id: str,
    ) -> ReasoningHistoryRecord | None:

        return self.history.get(incident_id)

    def list_history(
        self,
        limit: int | None = None,
    ) -> list[ReasoningHistoryRecord]:

        return self.history.list(limit=limit)

    def _emit(
        self,
        event_type: str,
        event: NormalizedEvent,
        *,
        agent: str,
        action: str,
        status: str = "",
        metadata: dict | None = None,
    ) -> None:
        """
        Publishes a command center event when a publisher is
        wired in. Non-fatal when unavailable.
        """

        if self.publisher is None:
            return

        try:

            from app.infrastructure.command_center.events import (
                CommandCenterEvent,
                EventType,
            )

            self.publisher.publish(
                CommandCenterEvent(
                    type=EventType(event_type),
                    incident_id=event.event_id,
                    agent=agent,
                    action=action,
                    status=status,
                    metadata=dict(metadata or {}),
                )
            )

        except Exception:
            pass
