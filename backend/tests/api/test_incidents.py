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
    assert isinstance(response.json(), list)


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