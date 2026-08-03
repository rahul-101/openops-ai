import asyncio

import pytest
from app.infrastructure.command_center.events import (
    CommandCenterEvent,
    EventCategory,
    EventPublisher,
    EventType,
)


def build_event(
    event_type: EventType,
    *,
    incident_id: str = "inc-1",
    agent: str = "planner",
    action: str = "analyze",
    status: str = "success",
    duration_ms: float = 0.0,
    metadata: dict | None = None,
) -> CommandCenterEvent:

    return CommandCenterEvent(
        type=event_type,
        incident_id=incident_id,
        agent=agent,
        action=action,
        status=status,
        duration_ms=duration_ms,
        metadata=dict(metadata or {}),
    )


# ==========================================================
# CommandCenterEvent
# ==========================================================


class TestCommandCenterEvent:

    def test_incident_category(self):

        event = build_event(EventType.INCIDENT_CREATED)

        assert event.category == EventCategory.INCIDENT

        resolved = build_event(EventType.INCIDENT_RESOLVED)

        assert resolved.category == EventCategory.INCIDENT

    def test_execution_category(self):

        started = build_event(EventType.TOOL_EXECUTION_STARTED)

        completed = build_event(
            EventType.TOOL_EXECUTION_COMPLETED,
        )

        assert started.category == EventCategory.EXECUTION

        assert completed.category == EventCategory.EXECUTION

    def test_agent_category(self):

        analysis = build_event(EventType.ANALYSIS_STARTED)

        decision = build_event(EventType.DECISION_CREATED)

        rca = build_event(EventType.RCA_COMPLETED)

        assert analysis.category == EventCategory.AGENT

        assert decision.category == EventCategory.AGENT

        assert rca.category == EventCategory.AGENT

    def test_unique_event_ids(self):

        first = build_event(EventType.ANALYSIS_STARTED)

        second = build_event(EventType.ANALYSIS_STARTED)

        assert first.event_id != second.event_id

    def test_to_dict_shape(self):

        event = build_event(
            EventType.DECISION_CREATED,
            metadata={"confidence": 0.9},
        )

        payload = event.to_dict()

        assert payload["type"] == "decision_created"

        assert payload["category"] == "agent"

        assert payload["incident_id"] == "inc-1"

        assert payload["agent"] == "planner"

        assert payload["action"] == "analyze"

        assert payload["status"] == "success"

        assert payload["metadata"] == {"confidence": 0.9}

        assert "timestamp" in payload

        assert "event_id" in payload


# ==========================================================
# EventPublisher
# ==========================================================


class TestEventPublisher:

    def test_publish_fanout_to_listeners(self):

        publisher = EventPublisher()

        received: list[CommandCenterEvent] = []

        publisher.subscribe(received.append)

        event = build_event(EventType.INCIDENT_CREATED)

        publisher.publish(event)

        assert received == [event]

    def test_unsubscribe_stops_delivery(self):

        publisher = EventPublisher()

        received: list[CommandCenterEvent] = []

        listener = received.append

        publisher.subscribe(listener)

        publisher.unsubscribe(listener)

        publisher.publish(build_event(EventType.INCIDENT_CREATED))

        assert received == []

    def test_listener_exception_does_not_break_publish(self):

        publisher = EventPublisher()

        def broken_listener(event):
            raise RuntimeError("boom")

        publisher.subscribe(broken_listener)

        received: list[CommandCenterEvent] = []

        publisher.subscribe(received.append)

        event = build_event(EventType.INCIDENT_CREATED)

        publisher.publish(event)

        assert received == [event]

    def test_publish_returns_event(self):

        publisher = EventPublisher()

        event = build_event(EventType.ANALYSIS_STARTED)

        assert publisher.publish(event) is event

    def test_history_returns_events_newest_last(self):

        publisher = EventPublisher()

        events = [
            build_event(
                EventType.ANALYSIS_STARTED,
                incident_id=f"inc-{i}",
            )
            for i in range(3)
        ]

        for event in events:
            publisher.publish(event)

        assert publisher.history() == events

    def test_history_limit(self):

        publisher = EventPublisher()

        for i in range(5):
            publisher.publish(
                build_event(
                    EventType.ANALYSIS_STARTED,
                    incident_id=f"inc-{i}",
                )
            )

        assert len(publisher.history(limit=2)) == 2

        assert publisher.history(limit=2)[-1].incident_id == "inc-4"

    def test_history_filter_by_event_type(self):

        publisher = EventPublisher()

        publisher.publish(build_event(EventType.INCIDENT_CREATED))

        publisher.publish(build_event(EventType.ANALYSIS_STARTED))

        publisher.publish(build_event(EventType.RCA_COMPLETED))

        filtered = publisher.history(
            event_type=EventType.ANALYSIS_STARTED,
        )

        assert len(filtered) == 1

        assert filtered[0].type == EventType.ANALYSIS_STARTED

    def test_history_filter_by_incident(self):

        publisher = EventPublisher()

        publisher.publish(
            build_event(
                EventType.ANALYSIS_STARTED,
                incident_id="inc-a",
            )
        )

        publisher.publish(
            build_event(
                EventType.ANALYSIS_STARTED,
                incident_id="inc-b",
            )
        )

        filtered = publisher.history(incident_id="inc-a")

        assert len(filtered) == 1

        assert filtered[0].incident_id == "inc-a"

    def test_history_bounded_deque(self):

        publisher = EventPublisher(max_history=3)

        for i in range(5):
            publisher.publish(
                build_event(
                    EventType.ANALYSIS_STARTED,
                    incident_id=f"inc-{i}",
                )
            )

        history = publisher.history()

        assert len(history) == 3

        assert history[0].incident_id == "inc-2"

    def test_clear_history(self):

        publisher = EventPublisher()

        publisher.publish(build_event(EventType.INCIDENT_CREATED))

        publisher.clear()

        assert publisher.history() == []


# ==========================================================
# Async Streaming
# ==========================================================


@pytest.mark.asyncio
class TestEventPublisherStreaming:

    async def test_stream_receives_published_event(self):

        publisher = EventPublisher()

        stream = publisher.open_stream()

        event = build_event(
            EventType.TOOL_EXECUTION_COMPLETED,
            status="success",
        )

        publisher.publish(event)

        payload = await asyncio.wait_for(
            stream.get(),
            timeout=1.0,
        )

        assert payload["event_id"] == event.event_id

        assert payload["type"] == "tool_execution_completed"

        publisher.close_stream(stream)

    async def test_closed_stream_not_delivered(self):

        publisher = EventPublisher()

        stream = publisher.open_stream()

        publisher.close_stream(stream)

        publisher.publish(build_event(EventType.ANALYSIS_STARTED))

        with pytest.raises(asyncio.TimeoutError):

            await asyncio.wait_for(
                stream.get(),
                timeout=0.05,
            )

    async def test_multiple_streams_receive_fanout(self):

        publisher = EventPublisher()

        first = publisher.open_stream()

        second = publisher.open_stream()

        publisher.publish(
            build_event(
                EventType.INCIDENT_CREATED,
                incident_id="inc-x",
            )
        )

        payload_one = await asyncio.wait_for(
            first.get(),
            timeout=1.0,
        )

        payload_two = await asyncio.wait_for(
            second.get(),
            timeout=1.0,
        )

        assert payload_one == payload_two

        assert payload_one["incident_id"] == "inc-x"

        publisher.close_stream(first)

        publisher.close_stream(second)
