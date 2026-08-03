from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


class TestProviderManagementAPI:

    def test_list_providers(self):

        with _client() as client:

            response = client.get("/providers")

            assert response.status_code == 200

            body = response.json()

            assert isinstance(body, list)

            names = {p["name"] for p in body}

            assert "gemini" in names

            assert "openrouter" in names

    def test_list_providers_include_metadata(self):

        with _client() as client:

            body = client.get("/providers").json()

            gemini = next(
                p for p in body if p["name"] == "gemini"
            )

            assert gemini["display_name"] == "Google Gemini"

            assert gemini["model"] != ""

            assert isinstance(gemini["priority"], int)

            assert "capabilities" in gemini

    def test_get_provider(self):

        with _client() as client:

            response = client.get("/providers/gemini")

            assert response.status_code == 200

            body = response.json()

            assert body["name"] == "gemini"

    def test_get_provider_not_found(self):

        with _client() as client:

            response = client.get("/providers/nonexistent")

            assert response.status_code == 404

    def test_get_provider_capabilities(self):

        with _client() as client:

            response = client.get(
                "/providers/gemini/capabilities"
            )

            assert response.status_code == 200

            body = response.json()

            assert isinstance(body, list)

            assert "text_generation" in body

    def test_get_provider_capabilities_not_found(self):

        with _client() as client:

            response = client.get(
                "/providers/nonexistent/capabilities"
            )

            assert response.status_code == 404
