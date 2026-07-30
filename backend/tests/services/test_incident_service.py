import pytest

from app.application.dto.requests.incident_request import UpdateIncidentRequest
from app.application.services.incident_service import IncidentService
from app.core.exceptions import ResourceNotFoundException
from app.domain.entities.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)


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

    page = service.list_incidents()

    assert page.total_items == 2
    assert page.page == 1
    assert page.size == 20
    assert len(page.items) == 2


def test_update_incident():
    service = create_service()

    incident = Incident(
        title="Database Down",
        description="Database unavailable",
        severity=IncidentSeverity.CRITICAL,
        source="Grafana",
    )

    service.create_incident(incident)

    request = UpdateIncidentRequest(
        title="Database Restored",
        description="Database recovered",
        severity=IncidentSeverity.LOW,
        status=IncidentStatus.RESOLVED,
        source="Grafana",
    )

    updated = service.update_incident(
        incident.id,
        request,
    )

    assert updated.id == incident.id
    assert updated.title == "Database Restored"
    assert updated.status == IncidentStatus.RESOLVED
    assert updated.severity == IncidentSeverity.LOW
    assert updated.created_at == incident.created_at
    assert updated.updated_at >= incident.updated_at


def test_update_nonexistent_incident():
    service = create_service()

    request = UpdateIncidentRequest(
        title="Test",
        description="Test description",
        severity=IncidentSeverity.LOW,
        status=IncidentStatus.OPEN,
        source="Test",
    )

    with pytest.raises(ResourceNotFoundException):
        service.update_incident(
            "does-not-exist",
            request,
        )


def test_delete_incident():
    service = create_service()

    incident = Incident(
        title="Memory Leak",
        description="Memory increasing",
        severity=IncidentSeverity.HIGH,
        source="Prometheus",
    )

    service.create_incident(incident)

    service.delete_incident(incident.id)

    with pytest.raises(ResourceNotFoundException):
        service.get_incident(incident.id)


def test_delete_nonexistent_incident():
    service = create_service()

    with pytest.raises(ResourceNotFoundException):
        service.delete_incident("does-not-exist")

def test_list_incidents_with_custom_page_size():
    service = create_service()

    for i in range(10):
        incident = Incident(
            title=f"Incident {i}",
            description="Test",
            severity=IncidentSeverity.LOW,
            source="Test",
        )

        service.create_incident(incident)

    page = service.list_incidents()

    assert page.total_items == 10
    assert page.page == 1