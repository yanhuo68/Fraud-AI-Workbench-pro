# tests/integration/test_api_ml.py
"""
Integration tests for the ML Model endpoints (api/routers/models.py):
  GET  /models/list      — list all registered models → {models: [...]}
  GET  /models/available — list all available LLMs → {llms: [...]}
  POST /models/score     — score using model_id + input_data (calls LLM/expert)
"""
import pytest
from unittest.mock import patch, MagicMock


def test_list_models(client, auth_headers):
    """GET /models/list should return 200 with a models list."""
    response = client.get("/models/list", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)


def test_list_models_unauthenticated(client):
    """GET /models/list without auth should return 401/403."""
    response = client.get("/models/list")
    assert response.status_code in (401, 403), response.text


def test_list_available_llms(client, auth_headers):
    """GET /models/available should return 200 with an llms list."""
    response = client.get("/models/available", headers=auth_headers)
    assert response.status_code in (200, 500)  # 500 OK if Ollama not running
    if response.status_code == 200:
        data = response.json()
        assert "llms" in data


def test_score_invalid_payload_missing_fields(client, auth_headers):
    """POST /models/score with empty body should return 422 (missing model_id)."""
    response = client.post("/models/score", headers=auth_headers, json={})
    assert response.status_code == 422, response.text


@patch("api.routers.models.init_llm")
def test_score_with_mock_llm(mock_init_llm, client, auth_headers):
    """POST /models/score with a mocked LLM should return a prediction string."""
    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = "HIGH_RISK: transaction appears fraudulent."
    mock_init_llm.return_value = fake_llm

    response = client.post(
        "/models/score",
        headers=auth_headers,
        json={
            "model_id": "mock-llm-model",
            "input_data": {"amount": 5000, "type": "CASH_OUT", "step": 1}
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], str)
    assert "metadata" in data



def test_score_unauthenticated(client):
    """POST /models/score without auth should return 401/403."""
    response = client.post(
        "/models/score",
        json={"model_id": "test", "input_data": "hello"}
    )
    assert response.status_code in (401, 403), response.text
