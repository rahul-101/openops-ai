from app.infrastructure.aiops.event_ingestion import (
    EventSeverity,
    NormalizedEvent,
)
from app.infrastructure.aiops.playbook_engine import (
    Playbook,
    PlaybookMatch,
    PlaybookStep,
    RemediationPlaybookEngine,
)

PLAYBOOK_YAML = """
name: kubernetes_crash_restart
description: Restart a crashing deployment
version: 1.0.0
match:
  source: kubernetes
  severities:
    - high
    - medium
  tags:
    - crash
    - restart
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
    auto_execute: true
  - name: restart_deployment
    tool: kubernetes
    action: restart
    risk_level: medium
    auto_execute: false
"""


def make_event(
    *,
    source: str = "kubernetes",
    severity: EventSeverity = EventSeverity.HIGH,
    tags: list[str] | None = None,
) -> NormalizedEvent:

    return NormalizedEvent(
        event_id="event-1",
        source=source,
        title="crash",
        severity=severity,
        tags=tags or ["crash"],
    )


def test_load_yaml():

    engine = RemediationPlaybookEngine()

    playbook = engine.load_yaml(PLAYBOOK_YAML)

    assert playbook.name == "kubernetes_crash_restart"
    assert playbook.version == "1.0.0"
    assert len(playbook.steps) == 2

    first = playbook.steps[0]

    assert first.tool == "kubernetes"
    assert first.action == "pod_status"
    assert first.risk_level == "low"
    assert first.auto_execute is True


def test_register_and_get():

    engine = RemediationPlaybookEngine()

    playbook = Playbook(
        name="simple",
        steps=[
            PlaybookStep(
                name="logs",
                tool="kubernetes",
                action="logs",
            )
        ],
    )

    engine.register(playbook)

    assert engine.get("simple") is playbook
    assert len(engine.list()) == 1


def test_find_matches_event():

    engine = RemediationPlaybookEngine()

    engine.load_yaml(PLAYBOOK_YAML)

    match = engine.find(make_event())

    assert match is not None
    assert match.name == "kubernetes_crash_restart"


def test_find_returns_none_when_source_mismatch():

    engine = RemediationPlaybookEngine()

    engine.load_yaml(PLAYBOOK_YAML)

    match = engine.find(
        make_event(source="datadog")
    )

    assert match is None


def test_find_returns_none_when_severity_mismatch():

    engine = RemediationPlaybookEngine()

    engine.load_yaml(PLAYBOOK_YAML)

    match = engine.find(
        make_event(severity=EventSeverity.LOW)
    )

    assert match is None


def test_find_returns_none_when_tag_mismatch():

    engine = RemediationPlaybookEngine()

    engine.load_yaml(PLAYBOOK_YAML)

    match = engine.find(
        make_event(tags=["memory"])
    )

    assert match is None


def test_match_missing_criteria_is_greedy():

    playbook = Playbook(
        name="greedy",
        match=PlaybookMatch(),
    )

    engine = RemediationPlaybookEngine()

    engine.register(playbook)

    assert engine.find(make_event()) is not None


def test_clear():

    engine = RemediationPlaybookEngine()

    engine.load_yaml(PLAYBOOK_YAML)

    engine.clear()

    assert engine.list() == []
