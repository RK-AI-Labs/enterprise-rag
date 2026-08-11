"""API tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_returns_200() -> None:
    """The health endpoint should report a healthy status with app metadata."""
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app_name" in body
    assert "environment" in body
