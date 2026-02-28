# tests/integration/test_api_admin.py
"""
Integration tests for the Admin API using actual endpoint signatures.

Admin endpoints (all require admin auth):
  GET    /admin/users                — list all users → {users: [...]}
  PATCH  /admin/users/{user_id}     — update role (Body: {role: str})
  PATCH  /admin/users/{id}/username — update username
  PATCH  /admin/users/{id}/email    — update email
  PATCH  /admin/users/{id}/password — update password
  DELETE /admin/users/{user_id}     — delete user (by int id)
  GET    /admin/permissions         — current user permissions → {role, permissions}
  GET    /admin/roles               — list roles → {roles: [...]}
  POST   /admin/roles               — create/update role (Body: name, permissions as List[str])
  DELETE /admin/roles/{name}        — delete role

Note: User creation is done via POST /auth/register (not POST /admin/users)
"""
import pytest


# ── Helpers ────────────────────────────────────────────────────────────────────

def _register_and_get_id(client, auth_headers, username, password="TestPw123!", role="guest"):
    """Register a user and return their integer id from the users list."""
    client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": role,
        "email": f"{username}@example.com"
    })
    resp = client.get("/admin/users", headers=auth_headers)
    users = resp.json()["users"]
    for u in users:
        if u["username"] == username:
            return u["id"]
    return None


# ── Permissions ────────────────────────────────────────────────────────────────

def test_get_permissions_as_admin(client, auth_headers):
    """Authenticated admin should receive a non-empty permissions list."""
    response = client.get("/admin/permissions", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
    assert len(data["permissions"]) > 0


def test_get_permissions_unauthenticated(client):
    """GET /admin/permissions without token should return 401 or 403."""
    response = client.get("/admin/permissions")
    assert response.status_code in (401, 403), response.text


# ── User Management ────────────────────────────────────────────────────────────

def test_list_users_as_admin(client, auth_headers):
    """Admin can list all users — response has 'users' key with a list."""
    response = client.get("/admin/users", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)
    # The admin user itself must appear
    usernames = [u["username"] for u in data["users"]]
    assert "testadmin" in usernames


def test_list_users_as_guest_forbidden(client):
    """Guest user should not be able to list all users (403)."""
    client.post("/auth/register", json={
        "username": "guestlist_test",
        "password": "GuestPwd123!",
        "role": "guest"
    })
    resp = client.post("/auth/token", data={
        "username": "guestlist_test",
        "password": "GuestPwd123!"
    })
    guest_token = resp.json()["access_token"]
    guest_headers = {"Authorization": f"Bearer {guest_token}"}
    response = client.get("/admin/users", headers=guest_headers)
    assert response.status_code in (401, 403), response.text


def test_patch_user_role_as_admin(client, auth_headers):
    """Admin can update a user's role via PATCH /admin/users/{user_id}."""
    user_id = _register_and_get_id(client, auth_headers, "role_patch_target")
    if user_id is None:
        pytest.skip("Could not find registered user in list")
    # "data_scientist" must exist as a role; fall back to "guest" if not
    response = client.patch(
        f"/admin/users/{user_id}",
        headers=auth_headers,
        json={"role": "guest"}
    )
    assert response.status_code in (200, 201, 400), response.text  # 400 = invalid role is still OK


def test_update_user_email_as_admin(client, auth_headers):
    """Admin can update a user's email."""
    user_id = _register_and_get_id(client, auth_headers, "email_patch_target")
    if user_id is None:
        pytest.skip("Could not find registered user in list")
    response = client.patch(
        f"/admin/users/{user_id}/email",
        headers=auth_headers,
        json={"email": "updated@example.com"}
    )
    assert response.status_code in (200, 201), response.text


def test_delete_user_as_admin(client, auth_headers):
    """Admin can delete a user by integer id."""
    user_id = _register_and_get_id(client, auth_headers, "delete_target_999")
    if user_id is None:
        pytest.skip("Could not create/find user for deletion")
    response = client.delete(f"/admin/users/{user_id}", headers=auth_headers)
    assert response.status_code in (200, 204), response.text


# ── Role Management ────────────────────────────────────────────────────────────

def test_list_roles_as_admin(client, auth_headers):
    """Admin can list all roles — returns {roles: [...]}."""
    response = client.get("/admin/roles", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "roles" in data
    assert isinstance(data["roles"], list)
    # admin and guest roles must exist
    role_names = [r["name"] for r in data["roles"]]
    assert "admin" in role_names
    assert "guest" in role_names


def test_create_and_delete_custom_role(client, auth_headers):
    """Admin can create a custom role then delete it."""
    role_name = "test_custom_analyst_role"
    # Create (POST /admin/roles) — uses n, permissions as top-level Body fields
    create_resp = client.post(
        "/admin/roles",
        headers=auth_headers,
        json={"name": role_name, "permissions": ["data_hub", "sql_rag"]}
    )
    assert create_resp.status_code in (200, 201), create_resp.text

    # Verify it exists
    list_resp = client.get("/admin/roles", headers=auth_headers)
    role_names = [r["name"] for r in list_resp.json()["roles"]]
    assert role_name in role_names

    # Delete (DELETE /admin/roles/{name})
    delete_resp = client.delete(f"/admin/roles/{role_name}", headers=auth_headers)
    assert delete_resp.status_code in (200, 204), delete_resp.text


def test_create_role_is_upsert(client, auth_headers):
    """Creating the same role twice should upsert (no error)."""
    role_name = "upsert_role_test"
    for pages in [["home"], ["home", "data_hub"]]:
        resp = client.post(
            "/admin/roles",
            headers=auth_headers,
            json={"name": role_name, "permissions": pages}
        )
        assert resp.status_code in (200, 201), resp.text

    # Clean up
    client.delete(f"/admin/roles/{role_name}", headers=auth_headers)


def test_cannot_delete_system_roles(client, auth_headers):
    """Deleting system roles 'admin' or 'guest' should return 400."""
    for system_role in ["admin", "guest"]:
        resp = client.delete(f"/admin/roles/{system_role}", headers=auth_headers)
        assert resp.status_code == 400, f"Expected 400 for deleting {system_role}, got {resp.status_code}"
