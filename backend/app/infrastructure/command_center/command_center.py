from app.infrastructure.command_center.activity_feed import (
    ActivityFeed,
    ActivitySnapshot,
)
from app.infrastructure.command_center.dashboard import (
    DashboardSnapshot,
    OperationsDashboard,
)
from app.infrastructure.command_center.events import (
    CommandCenterEvent,
    EventPublisher,
    EventType,
)
from app.infrastructure.command_center.execution_monitor import (
    ExecutionMonitor,
    ExecutionStatus,
)
from app.infrastructure.command_center.incident_timeline import (
    IncidentTimeline,
    TimelineEntry,
)


class OperationsCommandCenter:
    """
    Facade tying the real-time event publisher to the incident
    timeline, AI activity feed, execution monitor and operations
    dashboard.
    """

    def __init__(
        self,
        publisher: EventPublisher | None = None,
        timeline: IncidentTimeline | None = None,
        activity: ActivityFeed | None = None,
        monitor: ExecutionMonitor | None = None,
        dashboard: OperationsDashboard | None = None,
    ) -> None:

        self.publisher = publisher or EventPublisher()

        self.timeline = timeline or IncidentTimeline()

        self.activity = activity or ActivityFeed()

        self.monitor = monitor or ExecutionMonitor()

        self.dashboard = dashboard or OperationsDashboard()

        self.publisher.subscribe(self._on_event)

    # ==========================================================
    # Event Publishing
    # ==========================================================

    def emit(
        self,
        event_type: EventType,
        *,
        incident_id: str = "",
        agent: str = "",
        action: str = "",
        status: str = "",
        duration_ms: float = 0.0,
        metadata: dict | None = None,
    ) -> CommandCenterEvent:

        event = CommandCenterEvent(
            type=event_type,
            incident_id=incident_id,
            agent=agent,
            action=action,
            status=status,
            duration_ms=duration_ms,
            metadata=dict(metadata or {}),
        )

        return self.publisher.publish(event)

    def publish(
        self,
        event: CommandCenterEvent,
    ) -> CommandCenterEvent:

        return self.publisher.publish(event)

    # ==========================================================
    # Event Source (SSE)
    # ==========================================================

    def open_stream(self):

        return self.publisher.open_stream()

    def close_stream(self, stream):

        self.publisher.close_stream(stream)

    def history(
        self,
        limit: int | None = None,
        *,
        event_type: EventType | None = None,
        incident_id: str | None = None,
    ) -> list[CommandCenterEvent]:

        return self.publisher.history(
            limit,
            event_type=event_type,
            incident_id=incident_id,
        )

    # ==========================================================
    # Timeline
    # ==========================================================

    def get_timeline(
        self,
        incident_id: str,
    ) -> list[TimelineEntry]:

        return self.timeline.get(incident_id)

    def timeline_incidents(self) -> list[str]:

        return self.timeline.incidents()

    # ==========================================================
    # Activity Feed
    # ==========================================================

    def activity_snapshot(self) -> ActivitySnapshot:

        return self.activity.snapshot()

    # ==========================================================
    # Execution Monitor
    # ==========================================================

    def monitor_execution(
        self,
        agent: str,
        *,
        task: str = "",
        incident_id: str = "",
    ):

        return self.monitor.start(
            agent,
            task=task,
            incident_id=incident_id,
        )

    def complete_execution(
        self,
        execution_id: str,
        success: bool,
        *,
        duration_ms: float | None = None,
        error: str | None = None,
    ):

        return self.monitor.complete(
            execution_id,
            success,
            duration_ms=duration_ms,
            error=error,
        )

    def executions(
        self,
        status=None,
        incident_id: str | None = None,
    ) -> list:

        return self.monitor.list(
            status=status,
            incident_id=incident_id,
        )

    # ==========================================================
    # Dashboard
    # ==========================================================

    def dashboard_snapshot(self) -> DashboardSnapshot:

        return self.dashboard.snapshot()

    # ==========================================================
    # Event Routing
    # ==========================================================

    def _on_event(
        self,
        event: CommandCenterEvent,
    ) -> None:
        """
        Routes published events into the timeline, activity
        feed and dashboard.
        """

        if event.incident_id:
            self.timeline.record(
                event.incident_id,
                TimelineEntry(
                    timestamp=event.timestamp,
                    agent=event.agent,
                    action=event.action,
                    status=event.status,
                    duration_ms=event.duration_ms,
                    metadata={
                        "event_type": event.type.value,
                        **dict(event.metadata),
                    },
                ),
            )

        if event.type == EventType.TOOL_EXECUTION_STARTED:

            self.activity.agent_started(
                event.agent or "tool",
                task=event.action,
            )

            self.monitor.start(
                event.agent or "tool",
                task=event.action,
                incident_id=event.incident_id,
            )

        if event.type == EventType.TOOL_EXECUTION_COMPLETED:

            self.activity.record_action(
                event.status == "success",
                agent=event.agent,
                task=event.action,
            )

            self._complete_matching_execution(event)

        self.dashboard.record_event(event)

    def _complete_matching_execution(
        self,
        event: CommandCenterEvent,
    ) -> None:
        """
        Completes the running execution for the tool/incident
        that produced the completion event, when a matching
        running execution exists.
        """

        for execution in self.monitor.list(
            status=ExecutionStatus.RUNNING,
            incident_id=event.incident_id,
        ):

            if (
                execution.agent == event.agent
                and execution.task == event.action
            ):

                self.monitor.complete(
                    execution.execution_id,
                    success=event.status == "success",
                    duration_ms=(
                        event.duration_ms
                        if event.duration_ms > 0
                        else None
                    ),
                    error=(
                        event.metadata.get("error")
                        if event.status != "success"
                        else None
                    ),
                )

                return
