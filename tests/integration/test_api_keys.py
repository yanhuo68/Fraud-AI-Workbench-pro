# tests/integration/test_api_keys.py
"""
Integration tests for the API Key management endpoints (admin only):
  POST   /keys/generate   — generate a new API key  {name: str}
  GET    /keys/           — list all keys (partially masked)
  DELETE /keys/{key_id}  — revoke a key
"""
import pytest


def test_generate_api_key(client, auth_headers):
    """POST /keys/generate should return a new API key with id, name, key, created_at."""
    response = client.post("/keys/generate", headers=auth_headers, json={
        "name": "test-key"
    })
    assert response.status_code in (200, 201), response.text
    data = response.json()
    assert "key" in data
    assert data["key"].startswith("fl_")
    assert "id" in data
    assert "name" in data


def test_list_api_keys(client, auth_headers):
    """GET /keys/ should return a list of existing keys."""
    # Generate one first
    client.post("/keys/generate", headers=auth_headers, json={"name": "list-test"})
    response = client.get("/keys/", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)


def test_revoke_api_key(client, auth_headers):
    """DELETE /keys/{key_id} should revoke the key and return success."""
    # Generate a key first
    gen_resp = client.post("/keys/generate", headers=auth_headers, json={"name": "revoke-me"})
    assert gen_resp.status_code in (200, 201), gen_resp.text
    key_id = gen_resp.json()["id"]

    del_resp = client.delete(f"/keys/{key_id}", headers=auth_headers)
    assert del_resp.status_code in (200, 204), del_resp.text


def test_revoke_nonexistent_key_returns_404(client, auth_headers):
    """DELETE /keys/999999 for a key that doesn't exist should return 404."""
    response = client.delete("/keys/999999", headers=auth_headers)
    assert response.status_code == 404


def test_generate_key_unauthenticated(client):
    """POST /keys/generate without auth should fail (admin-only endpoint)."""
    response = client.post("/keys/generate", json={"name": "no-auth"})
    assert response.status_code in (401, 403, 422)
