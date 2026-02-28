import pytest
import os
import sqlite3
from fastapi.testclient import TestClient
from api.main import app
from config.settings import settings
from scripts.setup.init_users import init_user_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # Store original db path
    original_db = settings.db_path
    
    # Set to a temporary test database
    test_db = "test_rag.db"
    settings.db_path = test_db
    
    # Initialize with schema
    if os.path.exists(test_db):
        os.remove(test_db)
    
    init_user_db()
    
    yield
    
    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Restore original (though process will end)
    settings.db_path = original_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Helper to get auth headers for an admin user
    # Try to register/login a test admin
    username = "testadmin"
    password = "testpassword123"
    
    client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": "admin"
    })
    
    response = client.post("/auth/token", data={
        "username": username,
        "password": password
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
