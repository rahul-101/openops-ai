from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


class TestAIMonitoringAPI:

    def test_get_provider_health(self):

        with _client() as client:

            response = client.get("/ai/providers/health")

            assert response.status_code == 200

            assert isinstance(response.json(), list)

    def test_get_provider_metrics(self):

        with _client() as client:

            response = client.get("/ai/providers/metrics")

            assert response.status_code == 200

            assert isinstance(response.json(), list)
