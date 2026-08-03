from app.infrastructure.aiops.event_ingestion import (
    EventIngestionEngine,
    EventSeverity,
    RawAlert,
)


def test_ingest_alert_normalizes_event():

    engine = EventIngestionEngine()

    alert = RawAlert(
        source="prometheus",
        alert_id="alert-1",
        title="CPU spike detected",
        description="CPU at 95% on node-1",
        severity="critical",
        service="payments",
        tags=["cpu", "node"],
    )

    event = engine.ingest_alert(alert)

    assert event.event_id
    assert event.source == "prometheus"
    assert event.alert_id == "alert-1"
    assert event.title == "CPU spike detected"
    assert event.severity == EventSeverity.HIGH
    assert event.service == "payments"
    assert event.tags == ["cpu", "node"]


def test_ingest_keyword_api():

    engine = EventIngestionEngine()

    event = engine.ingest(
        source="datadog",
        alert_id="a-2",
        title="Memory pressure",
        severity="warning",
    )

    assert event.source == "datadog"
    assert event.severity == EventSeverity.MEDIUM


def test_severity_normalization():

    engine = EventIngestionEngine()

    assert (
        engine.ingest(
            source="s",
            alert_id="1",
            title="t",
            severity="p1",
        ).severity
        == EventSeverity.HIGH
    )

    assert (
        engine.ingest(
            source="s",
            alert_id="2",
            title="t",
            severity="info",
        ).severity
        == EventSeverity.LOW
    )

    assert (
        engine.ingest(
            source="s",
            alert_id="3",
            title="t",
            severity="unknown-thing",
        ).severity
        == EventSeverity.LOW
    )


def test_list_and_get():

    engine = EventIngestionEngine()

    a = engine.ingest(
        source="prometheus",
        alert_id="1",
        title="A",
        severity="high",
    )

    _ = engine.ingest(
        source="datadog",
        alert_id="2",
        title="B",
        severity="low",
    )

    assert len(engine.list()) == 2

    by_source = engine.list(source="prometheus")

    assert len(by_source) == 1
    assert by_source[0].alert_id == "1"

    by_severity = engine.list(
        severity=EventSeverity.LOW
    )

    assert len(by_severity) == 1
    assert by_severity[0].alert_id == "2"

    assert engine.get(a.event_id).title == "A"

    assert engine.get("missing") is None


def test_clear():

    engine = EventIngestionEngine()

    engine.ingest(
        source="prometheus",
        alert_id="1",
        title="A",
    )

    engine.clear()

    assert engine.list() == []
