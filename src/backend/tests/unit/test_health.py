"""Unit tests for the /health endpoint."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_body_structure():
    resp = client.get("/health")
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_no_auth_required():
    """Health endpoint must be accessible without Authorization header."""
    resp = client.get("/health", headers={})
    assert resp.status_code == 200
