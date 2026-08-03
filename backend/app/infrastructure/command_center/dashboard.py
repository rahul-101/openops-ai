from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from app.application.services.incident_service import IncidentService
from app.domain.entities.incident import IncidentStatus
from app.domain.models.incident_query import IncidentQuery
from app.infrastructure.learning.agent_analytics import (
    AgentAnalytics,
)
from app.infrastructure.reliability.rollback import (
    RemediationRollback,
)


@dataclass
class IncidentMetrics:
    """
    Aggregate incident KPIs.
    """

    total_incidents: int = 0

    resolved_incidents: int = 0

    auto_resolution_rate: float = 0.0

    average_resolution_time_s: float = 0.0

    open_incidents: int = 0


@dataclass
class AiMetrics:
    """
    Aggregate AI agent / model KPIs.
    """

    agent_success_rate: float = 0.0

    total_agent_runs: int = 0

    model_usage: dict = field(default_factory=dict)

    input_tokens: int = 0

    output_tokens: int = 0

    cost_usd: float = 0.0


@dataclass
class ExecutionMetrics:
    """
    Aggregate execution KPIs.
    """

    successful_actions: int = 0

    failed_actions: int = 0

    rollback_count: int = 0


@dataclass
class DashboardSnapshot:
    """
    Full operations dashboard snapshot.
    """

    incidents: IncidentMetrics = field(
        default_factory=IncidentMetrics
    )

    ai: AiMetrics = field(default_factory=AiMetrics)

    execution: ExecutionMetrics = field(
        default_factory=ExecutionMetrics
    )

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class OperationsDashboard:
    """
    Aggregates incident, AI and execution metrics for the
    operations dashboard.

    Incident KPIs come from the incident service/repository.
    AI KPIs are derived from tracked events (model usage,
    tokens, cost) combined with the agent analytics service.
    Execution KPIs are derived from tracked actions and the
    remediation rollback store.
    """

    def __init__(
        self,
        incident_service: IncidentService | None = None,
        agent_analytics: AgentAnalytics | None = None,
        rollback: RemediationRollback | None = None,
    ) -> None:

        self._incident_service = incident_service

        self._agent_analytics = agent_analytics

        self._rollback = rollback

        self._model_usage: dict[str, int] = {}

        self._input_tokens = 0

        self._output_tokens = 0

        self._cost_usd = 0.0

        self._successful_actions = 0

        self._failed_actions = 0

        self._lock = Lock()

    # ==========================================================
    # Event Recording
    # ==========================================================

    def record_event(
        self,
        event,
    ) -> None:
        """
        Updates tracked counters from a published event.
        """

        metadata = event.metadata or {}

        model = metadata.get("model")

        with self._lock:

            if model:
                self._model_usage[model] = (
                    self._model_usage.get(model, 0) + 1
                )

            self._input_tokens += int(
                metadata.get("input_tokens", 0)
            )

            self._output_tokens += int(
                metadata.get("output_tokens", 0)
            )

            self._cost_usd += float(
                metadata.get("cost_usd", 0.0)
            )

        from app.infrastructure.command_center.events import (
            EventType,
        )

        if event.type == EventType.TOOL_EXECUTION_COMPLETED:

            success = event.status == "success"

            with self._lock:

                if success:
                    self._successful_actions += 1
                else:
                    self._failed_actions += 1

    def record_ai_usage(
        self,
        *,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:

        with self._lock:

            if model:
                self._model_usage[model] = (
                    self._model_usage.get(model, 0) + 1
                )

            self._input_tokens += input_tokens

            self._output_tokens += output_tokens

            self._cost_usd += cost_usd

    # ==========================================================
    # Aggregates
    # ==========================================================

    def incident_metrics(self) -> IncidentMetrics:

        metrics = IncidentMetrics()

        if self._incident_service is None:
            return metrics

        incidents = self._incident_service.list_incidents(
            IncidentQuery(page=1, size=100)
        )

        metrics.total_incidents = incidents.total_items

        items = incidents.items

        metrics.resolved_incidents = sum(
            1
            for incident in items
            if incident.status == IncidentStatus.RESOLVED
        )

        metrics.open_incidents = sum(
            1
            for incident in items
            if incident.status != IncidentStatus.RESOLVED
        )

        metrics.auto_resolution_rate = (
            metrics.resolved_incidents
            / metrics.total_incidents
            * 100
            if metrics.total_incidents
            else 0.0
        )

        resolved = [
            incident
            for incident in items
            if incident.status == IncidentStatus.RESOLVED
            and incident.updated_at is not None
        ]

        if resolved:

            durations = [
                (incident.updated_at - incident.created_at).total_seconds()
                for incident in resolved
            ]

            metrics.average_resolution_time_s = (
                sum(durations) / len(durations)
            )

        return metrics

    def ai_metrics(self) -> AiMetrics:

        metrics = AiMetrics()

        with self._lock:

            metrics.model_usage = dict(self._model_usage)

            metrics.input_tokens = self._input_tokens

            metrics.output_tokens = self._output_tokens

            metrics.cost_usd = round(self._cost_usd, 6)

        if self._agent_analytics is not None:

            summary = self._agent_analytics.get_summary()

            metrics.total_agent_runs = summary.get(
                "total_runs",
                0,
            )

            metrics.agent_success_rate = round(
                summary.get("overall_success_rate", 0.0),
                2,
            )

        return metrics

    def execution_metrics(self) -> ExecutionMetrics:

        with self._lock:

            metrics = ExecutionMetrics(
                successful_actions=self._successful_actions,
                failed_actions=self._failed_actions,
            )

        if self._rollback is not None:

            metrics.rollback_count = len(
                self._rollback.list()
            )

        return metrics

    def snapshot(self) -> DashboardSnapshot:

        return DashboardSnapshot(
            incidents=self.incident_metrics(),
            ai=self.ai_metrics(),
            execution=self.execution_metrics(),
        )

    def clear(self) -> None:

        with self._lock:

            self._model_usage.clear()

            self._input_tokens = 0

            self._output_tokens = 0

            self._cost_usd = 0.0

            self._successful_actions = 0

            self._failed_actions = 0
