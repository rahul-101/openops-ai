from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Health check successful"
    assert body["data"]["status"] == "healthy"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["status"] == "running"

def test_demo_error_endpoint():
    response = client.get("/demo-error")

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Incident not found"
    assert body["data"] is None