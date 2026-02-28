import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "testpassword123",
        "role": "guest"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "guest"

def test_register_duplicate_user(client):
    # First registration
    client.post("/auth/register", json={
        "username": "duplicate",
        "password": "testpassword123",
        "role": "guest"
    })
    
    # Duplicate registration
    response = client.post("/auth/register", json={
        "username": "duplicate",
        "password": "anotherpassword",
        "role": "admin"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_success(client):
    # Register first
    username = "loginuser"
    password = "correctpassword"
    client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": "guest"
    })
    
    # Login
    response = client.post("/auth/token", data={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client):
    response = client.post("/auth/token", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
