from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock

from app.core.config import settings
from app.infrastructure.aiops.agents import (
    AIOpsContext,
    MultiAgentRunner,
)
from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
from app.infrastructure.aiops.event_ingestion import (
    EventIngestionEngine,
    NormalizedEvent,
    RawAlert,
)
from app.infrastructure.aiops.playbook_engine import (
    RemediationPlaybookEngine,
)
from app.infrastructure.learning.evaluation_engine import (
    EvaluationEngine,
)
from app.infrastructure.learning.feedback_engine import (
    FeedbackEngine,
)
from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)
from app.infrastructure.persistence.mongodb import get_database


class LifecycleStatus(str, Enum):
    """
    End-to-end lifecycle state of an incident.
    """

    INGESTED = "ingested"

    ANALYZED = "analyzed"

    REMEDIATED = "remediated"

    VERIFIED = "verified"

    UPDATED = "updated"

    LEARNED = "learned"

    COMPLETED = "completed"

    FAILED = "failed"


@dataclass
class LifecycleStep:
    """
    A single stage of the incident lifecycle.
    """

    stage: str

    status: str

    details: dict = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class LifecycleIncident:
    """
    Full E2E lifecycle record for an incident.
    """

    incident_id: str

    status: LifecycleStatus

    event: NormalizedEvent | None = None

    steps: list[LifecycleStep] = field(
        default_factory=list
    )

    servicenow_updated: bool = False

    learning_recorded: bool = False

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class IncidentLifecycleOrchestrator:
    """
    Runs the end-to-end incident lifecycle:

    Alert -> Analysis -> RCA -> Action -> Verification
    -> ServiceNow Update -> Learning
    """

    def __init__(
        self,
        ingestion: EventIngestionEngine,
        decision_engine: AutonomousDecisionEngine,
        playbooks: RemediationPlaybookEngine,
        agents: MultiAgentRunner,
        feedback: FeedbackEngine,
        evaluation: EvaluationEngine,
        executor=None,
        publisher=None,
    ) -> None:

        self.ingestion = ingestion
        self.decision_engine = decision_engine
        self.playbooks = playbooks
        self.agents = agents
        self.feedback = feedback
        self.evaluation = evaluation
        self.executor = executor
        self.publisher = publisher

        self._incidents: dict[str, LifecycleIncident] = {}

        self._lock = Lock()

        self._store = new_store("lifecycle")

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.aiops.mongo_lifecycle_repository import (
                MongoLifecycleRepository,
            )
            self._mongo_repo = MongoLifecycleRepository()
            # Load from MongoDB
            for incident in self._mongo_repo.list():
                self._incidents[incident.incident_id] = incident

        if self._store is not None:

            for record in self._store.all():

                incident = from_jsonable(
                    record,
                    LifecycleIncident,
                )

                if incident is not None:
                    self._incidents[incident.incident_id] = incident

    def _persist(
        self,
        incident: LifecycleIncident,
    ) -> None:

        if self._store is not None:
            self._store.save(
                incident.incident_id,
                to_jsonable(incident),
            )

    async def handle_alert(
        self,
        alert: RawAlert,
    ) -> LifecycleIncident:
        """
        Processes a raw alert through the full lifecycle.
        """

        event = self.ingestion.ingest_alert(alert)

        incident = LifecycleIncident(
            incident_id=event.event_id,
            status=LifecycleStatus.INGESTED,
            event=event,
        )

        self._emit(
            "incident_created",
            event.event_id,
            agent="ingestion",
            action="ingest",
            status="success",
            metadata={
                "source": event.source,
                "severity": event.severity.value,
            },
        )

        self._add_step(
            incident,
            "ingestion",
            "ingested",
            {
                "source": event.source,
                "severity": event.severity.value,
            },
        )

        # =====================================================
        # Analysis + RCA + Action (multi-agent flow)
        # =====================================================

        self._emit(
            "analysis_started",
            event.event_id,
            agent="incident",
            action="analyze",
        )

        playbook = self.playbooks.find(event)

        decision = self.decision_engine.decide(
            event,
            playbook,
        )

        incident.status = LifecycleStatus.ANALYZED

        self._emit(
            "decision_created",
            event.event_id,
            agent="planner",
            action=decision.playbook or "none",
            status="created",
            metadata={
                "category": decision.analysis.category,
                "recommendation": (
                    decision.analysis.recommendation
                ),
                "confidence": decision.analysis.confidence,
            },
        )

        self._add_step(
            incident,
            "analysis",
            "analyzed",
            {
                "category": decision.analysis.category,
                "probable_cause": (
                    decision.analysis.probable_cause
                ),
                "confidence": decision.analysis.confidence,
            },
        )

        context = AIOpsContext(
            event=event,
            analysis=decision.analysis,
            decision=decision,
            incident_id=event.event_id,
        )

        self._emit(
            "rca_completed",
            event.event_id,
            agent="rca",
            action="analyze",
            status="success",
            metadata={
                "probable_cause": (
                    decision.analysis.probable_cause
                ),
            },
        )

        for action in decision.actions:

            self._emit(
                "tool_execution_started",
                event.event_id,
                agent=action.tool,
                action=action.action,
            )

        await self.agents.run(context)

        for result in context.execution_results:

            self._emit(
                "tool_execution_completed",
                event.event_id,
                agent=result.get("tool", ""),
                action=result.get("action", ""),
                status=(
                    "success"
                    if result.get("success")
                    else "failure"
                ),
                duration_ms=result.get("duration_ms", 0.0),
                metadata={
                    "error": result.get("error"),
                },
            )

        self._add_step(
            incident,
            "remediation",
            "executed",
            {
                "playbook": decision.playbook,
                "execution": context.execution_results,
            },
        )

        verified = context.verification.get("resolved", False)

        incident.status = (
            LifecycleStatus.VERIFIED
            if verified
            else LifecycleStatus.FAILED
        )

        if verified:
            self._emit(
                "incident_resolved",
                event.event_id,
                agent="verification",
                action="resolve",
                status="success",
            )

        self._add_step(
            incident,
            "verification",
            (
                "verified"
                if verified
                else "failed"
            ),
            dict(context.verification),
        )

        # =====================================================
        # ServiceNow Update
        # =====================================================

        if self.executor is not None:

            servicenow_result = await self._update_servicenow(
                event,
                decision,
            )

            incident.servicenow_updated = (
                servicenow_result
            )

            self._add_step(
                incident,
                "servicenow",
                (
                    "updated"
                    if servicenow_result
                    else "skipped"
                ),
                {"updated": servicenow_result},
            )

        # =====================================================
        # Learning
        # =====================================================

        self._record_learning(
            event,
            decision,
            verified,
        )

        incident.learning_recorded = True

        incident.status = LifecycleStatus.COMPLETED

        self._add_step(
            incident,
            "learning",
            "recorded",
            {
                "outcome": (
                    "success" if verified else "failure"
                ),
            },
        )

        with self._lock:
            self._incidents[incident.incident_id] = incident

        self._persist(incident)

        return incident

    def get(
        self,
        incident_id: str,
    ) -> LifecycleIncident | None:

        with self._lock:
            return self._incidents.get(incident_id)

    def list(self) -> list[LifecycleIncident]:

        with self._lock:
            return list(self._incidents.values())

    def clear(self) -> None:

        with self._lock:
            self._incidents.clear()

        if self._store is not None:
            self._store.clear()

    # ==========================================================
    # Helpers
    # ==========================================================

    async def _update_servicenow(
        self,
        event: NormalizedEvent,
        decision,
    ) -> bool:
        """
        Creates or updates a ServiceNow incident via the tool
        executor. Non-fatal on failure.
        """

        try:

            from app.infrastructure.tools.models import (
                ToolExecutionContext,
            )

            result = await self.executor.execute(
                tool_name="servicenow",
                parameters={
                    "action": "create_incident",
                    "short_description": event.title,
                    "description": event.description,
                    "category": decision.analysis.category,
                    "impact": (
                        "1"
                        if event.severity.value == "high"
                        else "2"
                    ),
                    "urgency": (
                        "1"
                        if event.severity.value == "high"
                        else "2"
                    ),
                },
                context=ToolExecutionContext(
                    incident_id=event.event_id,
                ),
            )

            return result.success

        except Exception:

            return False

    def _record_learning(
        self,
        event: NormalizedEvent,
        decision,
        verified: bool,
    ) -> None:
        """
        Records feedback and evaluation for the learning
        engine.
        """

        outcome = "success" if verified else "failure"

        self.feedback.record_outcome(
            recommendation_id=event.event_id,
            outcome=outcome,
            incident_id=event.event_id,
            agent="aiops-lifecycle",
            model="rule-based",
            playbook=decision.playbook,
        )

        self.evaluation.record_evaluation(
            incident_id=event.event_id,
            rca_accurate=verified,
            remediation_success=verified,
            confidence=decision.analysis.confidence,
            outcome=verified,
        )

    @staticmethod
    def _add_step(
        incident: LifecycleIncident,
        stage: str,
        status: str,
        details: dict,
    ) -> None:

        incident.steps.append(
            LifecycleStep(
                stage=stage,
                status=status,
                details=details,
            )
        )

        incident.updated_at = datetime.utcnow()

    def _emit(
        self,
        event_type: str,
        incident_id: str,
        *,
        agent: str,
        action: str,
        status: str = "",
        duration_ms: float = 0.0,
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
                    incident_id=incident_id,
                    agent=agent,
                    action=action,
                    status=status,
                    duration_ms=duration_ms,
                    metadata=dict(metadata or {}),
                )
            )

        except Exception:
            pass
