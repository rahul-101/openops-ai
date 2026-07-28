import pytest

from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import (
    Incident,
    IncidentSeverity,
)
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)
from app.application.services.incident_service import IncidentService


def create_service() -> IncidentService:
    """
    Create a fresh IncidentService with a new in-memory repository.
    Each test gets its own isolated storage.
    """
    repository = InMemoryIncidentRepository()
    return IncidentService(repository)


def test_create_incident():
    service = create_service()

    incident = Incident(
        title="CPU High",
        description="CPU usage exceeded 90%",
        severity=IncidentSeverity.HIGH,
        source="Prometheus",
    )

    created = service.create_incident(incident)

    assert created.id == incident.id
    assert created.title == "CPU High"


def test_get_incident():
    service = create_service()

    incident = Incident(
        title="Database Down",
        description="Database unavailable",
        severity=IncidentSeverity.CRITICAL,
        source="Grafana",
    )

    service.create_incident(incident)

    retrieved = service.get_incident(incident.id)

    assert retrieved.id == incident.id
    assert retrieved.title == incident.title


def test_get_nonexistent_incident():
    service = create_service()

    with pytest.raises(ResourceNotFoundException):
        service.get_incident("does-not-exist")


def test_list_incidents():
    service = create_service()

    first = Incident(
        title="API Error",
        description="500 responses",
        severity=IncidentSeverity.HIGH,
        source="NGINX",
    )

    second = Incident(
        title="Disk Full",
        description="Disk utilization exceeded threshold",
        severity=IncidentSeverity.CRITICAL,
        source="Prometheus",
    )

    service.create_incident(first)
    service.create_incident(second)

    incidents = service.list_incidents()

    assert len(incidents) == 2