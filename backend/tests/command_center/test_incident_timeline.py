from datetime import UTC, datetime

from app.infrastructure.command_center.incident_timeline import (
    IncidentTimeline,
    TimelineEntry,
)


def build_entry(
    *,
    agent: str = "planner",
    action: str = "analyze",
    status: str = "success",
) -> TimelineEntry:

    return TimelineEntry(
        timestamp=datetime.now(UTC),
        agent=agent,
        action=action,
        status=status,
        metadata={"event_type": "analysis_started"},
    )


class TestIncidentTimeline:

    def test_record_and_get(self):

        timeline = IncidentTimeline()

        timeline.record("inc-1", build_entry())

        entries = timeline.get("inc-1")

        assert len(entries) == 1

        assert entries[0].agent == "planner"

    def test_get_unknown_incident_returns_empty(self):

        timeline = IncidentTimeline()

        assert timeline.get("missing") == []

    def test_entries_preserved_in_order(self):

        timeline = IncidentTimeline()

        for i in range(3):
            timeline.record(
                "inc-1",
                build_entry(action=f"step-{i}"),
            )

        actions = [
            entry.action
            for entry in timeline.get("inc-1")
        ]

        assert actions == ["step-0", "step-1", "step-2"]

    def test_incidents_lists_tracked_ids(self):

        timeline = IncidentTimeline()

        timeline.record("inc-a", build_entry())

        timeline.record("inc-b", build_entry())

        assert sorted(timeline.incidents()) == [
            "inc-a",
            "inc-b",
        ]

    def test_incidents_deduplicated(self):

        timeline = IncidentTimeline()

        timeline.record("inc-a", build_entry())

        timeline.record("inc-a", build_entry())

        assert timeline.incidents() == ["inc-a"]

    def test_entry_to_dict_shape(self):

        entry = build_entry()

        payload = entry.to_dict()

        assert payload["agent"] == "planner"

        assert payload["action"] == "analyze"

        assert payload["status"] == "success"

        assert payload["metadata"]["event_type"] == "analysis_started"

        assert "timestamp" in payload

    def test_clear_wipes_everything(self):

        timeline = IncidentTimeline()

        timeline.record("inc-1", build_entry())

        timeline.clear()

        assert timeline.incidents() == []

        assert timeline.get("inc-1") == []
