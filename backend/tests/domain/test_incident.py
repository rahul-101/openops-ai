from app.domain.entities.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)


def test_create_incident():
    incident = Incident(
        title="Database Down",
        description="Production database is unavailable",
        severity=IncidentSeverity.CRITICAL,
        source="monitoring",
    )

    assert incident.title == "Database Down"
    assert incident.status == IncidentStatus.OPEN
    assert incident.id is not None
    assert incident.created_at is not None