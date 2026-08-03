from app.infrastructure.reliability.incident_correlation import (
    CorrelationMethod,
    IncidentCorrelation,
)


def test_exact_duplicate_detected():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="checkout",
        tags=["cpu", "high"],
    )

    result = correlation.correlate(
        incident_id="inc-2",
        source="prometheus",
        service="checkout",
        tags=["cpu", "high"],
    )

    assert result.duplicate is True
    assert result.method == CorrelationMethod.EXACT_DUPLICATE
    assert result.matches == ["inc-1"]


def test_duplicate_does_not_match_different_tags():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="checkout",
        tags=["cpu"],
    )

    result = correlation.correlate(
        incident_id="inc-2",
        source="prometheus",
        service="checkout",
        tags=["memory"],
    )

    assert result.duplicate is False


def test_related_by_shared_service():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="database",
        tags=["cpu"],
    )

    correlation.merge("inc-1", "inc-3")

    result = correlation.correlate(
        incident_id="inc-2",
        source="datadog",
        service="database",
        tags=["memory"],
    )

    assert result.duplicate is False
    assert result.group_id is not None
    assert result.method == CorrelationMethod.SHARED_SERVICE


def test_related_by_shared_tag():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="checkout",
        tags=["network"],
    )

    correlation.merge("inc-1", "inc-3")

    result = correlation.correlate(
        incident_id="inc-2",
        source="datadog",
        service="payments",
        tags=["network"],
    )

    assert result.duplicate is False
    assert result.group_id is not None
    assert result.method == CorrelationMethod.SHARED_TAG


def test_no_relation_returns_isolated():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="checkout",
        tags=["cpu"],
    )

    result = correlation.correlate(
        incident_id="inc-2",
        source="datadog",
        service="payments",
        tags=["memory"],
    )

    assert result.duplicate is False
    assert result.group_id is None


def test_merge_groups_incidents():

    correlation = IncidentCorrelation()

    group = correlation.merge("inc-1", "inc-2")

    assert group.primary_incident == "inc-1"
    assert group.incidents == ["inc-1", "inc-2"]

    stored = correlation.get_group(group.id)

    assert stored is not None


def test_clear():

    correlation = IncidentCorrelation()

    correlation.register_incident(
        incident_id="inc-1",
        source="prometheus",
        service="checkout",
    )

    correlation.merge("inc-1", "inc-2")

    correlation.clear()

    assert correlation.list_groups() == []
