# tests/integration/test_api_health.py
"""
Integration tests for the Health endpoint: GET /health.
"""
import pytest


def test_health_returns_ok(client):
    """GET /health must return HTTP 200 and {status: ok}."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_is_public(client):
    """GET /health should be accessible without an auth token."""
    # No Authorization header — should still return 200
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_is_json(client):
    """GET /health response Content-Type must be application/json."""
    response = client.get("/health")
    assert "application/json" in response.headers.get("content-type", "")
