from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_incident():
    payload = {
        "title": "Database Down",
        "description": "Primary database unavailable",
        "severity": "CRITICAL",
        "source": "Prometheus",
    }

    response = client.post("/incidents", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == payload["title"]
    assert body["severity"] == "CRITICAL"


def test_list_incidents():
    response = client.get("/incidents")

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert "page" in body
    assert "size" in body
    assert "total_items" in body
    assert "total_pages" in body
    assert "has_next" in body
    assert "has_previous" in body

    assert isinstance(body["items"], list)
    assert body["page"] == 1
    assert body["size"] == 20


def test_get_incident():
    payload = {
        "title": "API Failure",
        "description": "500 errors",
        "severity": "HIGH",
        "source": "Grafana",
    }

    created = client.post("/incidents", json=payload).json()

    response = client.get(f"/incidents/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_incident():
    payload = {
        "title": "Database Down",
        "description": "Primary database unavailable",
        "severity": "CRITICAL",
        "source": "Prometheus",
    }

    created = client.post("/incidents", json=payload).json()

    update_payload = {
        "title": "Database Restored",
        "description": "Database is healthy again",
        "severity": "LOW",
        "status": "RESOLVED",
        "source": "Prometheus",
    }

    response = client.put(
        f"/incidents/{created['id']}",
        json=update_payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created["id"]
    assert body["title"] == "Database Restored"
    assert body["status"] == "RESOLVED"
    assert body["severity"] == "LOW"
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] != created["updated_at"]


def test_delete_incident():
    payload = {
        "title": "Memory Leak",
        "description": "Memory usage increasing",
        "severity": "HIGH",
        "source": "Grafana",
    }

    created = client.post("/incidents", json=payload).json()

    response = client.delete(f"/incidents/{created['id']}")

    assert response.status_code == 204
    assert response.text == ""

    response = client.get(f"/incidents/{created['id']}")

    assert response.status_code == 404


def test_update_nonexistent_incident():
    payload = {
        "title": "Unknown",
        "description": "Unknown",
        "severity": "LOW",
        "status": "OPEN",
        "source": "Test",
    }

    response = client.put(
        "/incidents/does-not-exist",
        json=payload,
    )

    assert response.status_code == 404


def test_delete_nonexistent_incident():
    response = client.delete("/incidents/does-not-exist")

    assert response.status_code == 404

def test_list_incidents_with_pagination():
    """
    Verify pagination metadata is returned.
    """

    response = client.get(
        "/incidents?page=1&size=5"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["page"] == 1
    assert body["size"] == 5

    assert "total_items" in body
    assert "total_pages" in body
    assert "has_next" in body
    assert "has_previous" in body

def test_list_incidents_invalid_page():
    response = client.get(
        "/incidents?page=0"
    )

    assert response.status_code == 422

def test_list_incidents_invalid_order():
    response = client.get(
        "/incidents?order=random"
    )

    assert response.status_code == 422
