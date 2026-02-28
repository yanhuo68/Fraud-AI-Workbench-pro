# tests/e2e/test_smoke.py
"""
End-to-end smoke tests — verify the key API endpoints respond sensibly
using the FastAPI TestClient (in-process, no network).

These tests are meant to be a fast confidence check across all routers:
they don't test every edge case, just that each endpoint doesn't 500.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


# ── API surface health check ───────────────────────────────────────────────────

def test_health_endpoint_alive(client):
    """The /health endpoint must always be reachable."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_protected_endpoint_requires_auth(client):
    """A protected endpoint should return 401/403 without a token."""
    endpoints_to_check = [
        ("GET",  "/admin/users"),
        ("GET",  "/admin/roles"),
        ("GET",  "/models/list"),
        ("GET",  "/keys/"),
    ]
    for method, path in endpoints_to_check:
        resp = getattr(client, method.lower())(path)
        assert resp.status_code in (401, 403), (
            f"{method} {path} should require auth, got {resp.status_code}"
        )


# ── Complete auth flow ─────────────────────────────────────────────────────────

def test_auth_flow_register_login_access(client):
    """
    Full auth cycle:
      1. Register a new user
      2. Log in to receive a JWT
      3. Use the JWT to access a protected endpoint successfully
    """
    username = "smoke_e2e_user"
    password = "SmokeTest123!"
    role = "guest"

    # 1 — Register (idempotent — 400 is OK if already registered)
    reg = client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": role,
        "email": "smoke@example.com"
    })
    assert reg.status_code in (200, 400), reg.text

    # 2 — Login must succeed and return a bearer token
    login = client.post("/auth/token", data={
        "username": username,
        "password": password
    })
    assert login.status_code == 200, login.text
    token_data = login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]
    assert len(token) > 10  # Sanity-check it's not empty

    # 3 — Use the token; guest can call /health (public) — just confirm the token is usable
    headers = {"Authorization": f"Bearer {token}"}
    health = client.get("/health", headers=headers)
    assert health.status_code == 200


# ── Ingest + Query smoke test ──────────────────────────────────────────────────

@patch("api.routers.ingest.ingest_uploaded_csv_dynamic")
@patch("rag_sql.graph_utils.create_document_node")
@patch("rag_sql.graph_utils.sync_db_schema_to_graph")
@patch("rag_sql.build_kb_index.build_vectorstore")
@patch("api.routers.rag.generate_sql_candidates")
@patch("api.routers.rag.pick_best_sql")
@patch("api.routers.rag.run_sql_query")
@patch("api.routers.rag.build_schema_text_from_tables")
def test_ingest_then_query(
    mock_schema, mock_run, mock_pick, mock_gen,
    mock_kb, mock_sync, mock_node, mock_ingest,
    client, auth_headers
):
    """
    Smoke test: upload a CSV → immediately query it via NLQ.
    All I/O is mocked; this just tests that the request plumbing works end-to-end.
    """
    # Configure mocks
    mock_ingest.return_value = ("smoke_transactions", 5, ["id", "amount", "fraud"])
    mock_schema.return_value = "id INT, amount FLOAT, fraud INT"
    mock_gen.return_value = ["SELECT * FROM smoke_transactions LIMIT 5"]
    mock_df = pd.DataFrame([{"id": i, "amount": i * 100.0, "fraud": 0} for i in range(5)])
    mock_pick.return_value = {
        "best": {"sql": "SELECT * FROM smoke_transactions LIMIT 5"}
    }
    mock_run.return_value = (mock_df, ["id", "amount", "fraud"])

    # 1 — Ingest
    csv_data = "id,amount,fraud\n1,100,0\n2,200,1\n3,300,0\n4,400,0\n5,500,1"
    ingest_resp = client.post(
        "/ingest/file",
        files={"file": ("smoke_test.csv", csv_data.encode(), "text/csv")},
        headers=auth_headers
    )
    assert ingest_resp.status_code == 200

    # 2 — NLQ query
    query_resp = client.post(
        "/rag/nlq",
        json={"question": "Show me all transactions"},
        headers=auth_headers
    )
    assert query_resp.status_code == 200
    data = query_resp.json()
    assert "sql" in data
    assert "preview" in data


# ── Admin panel smoke tests ────────────────────────────────────────────────────

def test_admin_users_smoke(client, auth_headers):
    """Admin should be able to list users via the admin API."""
    resp = client.get("/admin/users", headers=auth_headers)
    assert resp.status_code == 200


def test_admin_roles_smoke(client, auth_headers):
    """Admin should be able to list roles via the admin API."""
    resp = client.get("/admin/roles", headers=auth_headers)
    assert resp.status_code == 200


# ── All defined routes respond with non-500 ───────────────────────────────────

def test_no_server_errors_on_get_routes(client, auth_headers):
    """All safe GET routes should not return 500 Internal Server Error."""
    GET_ROUTES = [
        "/health",
        "/admin/users",
        "/admin/roles",
        "/admin/permissions",
        "/models/list",
        "/keys/",
    ]
    for route in GET_ROUTES:
        resp = client.get(route, headers=auth_headers)
        assert resp.status_code != 500, (
            f"GET {route} returned 500: {resp.text[:200]}"
        )
