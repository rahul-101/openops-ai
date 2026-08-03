from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


class TestKnowledgeAPI:

    def test_store_runbook(self):

        with _client() as client:

            response = client.post(
                "/knowledge/runbooks",
                json={
                    "title": "DB Recovery",
                    "content": "Restart the replica set.",
                    "metadata": {"service": "db"},
                },
            )

            assert response.status_code == 200

            body = response.json()

            assert body["title"] == "DB Recovery"

            assert body["type"] == "runbook"

            assert body["id"]

    def test_store_runbook_requires_content(self):

        with _client() as client:

            response = client.post(
                "/knowledge/runbooks",
                json={"title": "Missing content"},
            )

            assert response.status_code == 422

    def test_store_resolution(self):

        with _client() as client:

            response = client.post(
                "/knowledge/resolutions",
                json={
                    "title": "Resolved outage",
                    "content": "Rolled back the bad deploy.",
                },
            )

            assert response.status_code == 200

            assert response.json()["type"] == "resolution"

    def test_store_incident(self):

        with _client() as client:

            response = client.post(
                "/knowledge/incidents",
                json={
                    "title": "Disk full",
                    "description": "Filesystem at 100%",
                    "category": "storage",
                    "severity": "HIGH",
                },
            )

            assert response.status_code == 200

            assert response.json()["type"] == "incident"

    def test_get_document(self):

        with _client() as client:

            created = client.post(
                "/knowledge/runbooks",
                json={"title": "Net", "content": "Restart switch."},
            ).json()

            response = client.get(
                f"/knowledge/documents/{created['id']}"
            )

            assert response.status_code == 200

            assert response.json()["id"] == created["id"]

    def test_get_document_not_found(self):

        with _client() as client:

            response = client.get(
                "/knowledge/documents/nope"
            )

            assert response.status_code == 404

    def test_delete_document(self):

        with _client() as client:

            created = client.post(
                "/knowledge/runbooks",
                json={"title": "Net", "content": "Restart."},
            ).json()

            response = client.delete(
                f"/knowledge/documents/{created['id']}"
            )

            assert response.status_code == 200

            assert response.json()["deleted"] == created["id"]

            missing = client.get(
                f"/knowledge/documents/{created['id']}"
            )

            assert missing.status_code == 404

    def test_search(self):

        with _client() as client:

            response = client.get(
                "/knowledge/search?q=database&limit=3"
            )

            assert response.status_code == 200

            assert isinstance(response.json(), list)

    def test_ingest(self):

        with _client() as client:

            response = client.post(
                "/knowledge/ingest",
                json={
                    "title": "Long guide",
                    "content": " ".join(["word"] * 300),
                    "type": "runbook",
                },
            )

            assert response.status_code == 200

            docs = response.json()

            assert isinstance(docs, list)
            assert len(docs) > 1

    def test_ingest_invalid_type(self):

        with _client() as client:

            response = client.post(
                "/knowledge/ingest",
                json={
                    "title": "X",
                    "content": "y",
                    "type": "bogus",
                },
            )

            assert response.status_code == 422

    def test_save_and_get_incident_memory(self):

        with _client() as client:

            saved = client.post(
                "/knowledge/memory",
                json={
                    "incident_id": "INC-7",
                    "root_cause": "Config drift",
                    "recommendation": "Pin configs",
                    "final_resolution": "Applied pinning",
                },
            )

            assert saved.status_code == 200
            assert saved.json()["incident_id"] == "INC-7"

            fetched = client.get("/knowledge/memory/INC-7")

            assert fetched.status_code == 200
            assert fetched.json()["root_cause"] == "Config drift"

    def test_get_incident_memory_not_found(self):

        with _client() as client:

            response = client.get("/knowledge/memory/UNKNOWN")

            assert response.status_code == 404
