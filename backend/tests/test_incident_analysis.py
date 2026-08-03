from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch(
    "app.application.services.incident_analysis_service.IncidentAnalysisService.analyze",
    new_callable=AsyncMock,
)
def test_analyze_incident_success(mock_analyze):

    mock_analyze.return_value = {
        "summary": "Database latency detected.",
        "severity": "HIGH",
        "category": "Database",
        "probable_cause": "High CPU utilization on DB server.",
        "recommendation": "Scale database resources and investigate long-running queries.",
        "confidence": 0.96,
        "provider": "Gemini",
        "model": "gemini-2.5-flash",
        "input_tokens": 125,
        "output_tokens": 82,
        "processing_time_ms": 245.6,
    }

    response = client.post(
        "/incidents/analyze",
        json={
            "title": "Database latency",
            "description": "Users experience timeout while accessing dashboard.",
            "severity": "HIGH",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["summary"] == "Database latency detected."
    assert body["severity"] == "HIGH"
    assert body["category"] == "Database"
    assert body["probable_cause"] == "High CPU utilization on DB server."
    assert body["provider"] == "Gemini"
    assert body["model"] == "gemini-2.5-flash"
    assert body["confidence"] == 0.96
