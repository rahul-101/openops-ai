from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


class TestRoutingAPI:

    def test_get_provider_priority(self):

        with _client() as client:

            response = client.get("/routing/priority")

            assert response.status_code == 200

            body = response.json()

            assert "providers" in body

            assert isinstance(body["providers"], list)

            assert "gemini" in body["providers"]

    def test_get_ranked_providers(self):

        with _client() as client:

            response = client.get("/routing/ranked")

            assert response.status_code == 200

            body = response.json()

            assert isinstance(body["providers"], list)
