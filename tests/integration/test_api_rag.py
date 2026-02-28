import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

@patch("api.routers.rag.build_schema_text_from_tables")
@patch("api.routers.rag.generate_sql_candidates")
@patch("api.routers.rag.pick_best_sql")
@patch("api.routers.rag.run_sql_query")
def test_nlq_success(
    mock_run, mock_pick, mock_gen, mock_schema, 
    client, auth_headers
):
    # Setup mocks
    mock_schema.return_value = "Column: id (INT), Column: amount (FLOAT)"
    mock_gen.return_value = ["SELECT * FROM transactions LIMIT 5"]
    mock_pick.return_value = {"best": {"sql": "SELECT * FROM transactions LIMIT 5"}}
    
    mock_df = pd.DataFrame([{"id": 1, "amount": 100.0}])
    mock_run.return_value = (mock_df, ["id", "amount"])
    
    response = client.post(
        "/rag/nlq",
        json={"question": "Show me some transactions"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sql"] == "SELECT * FROM transactions LIMIT 5"
    assert len(data["preview"]) == 1
    assert data["columns"] == ["id", "amount"]

@patch("api.routers.agents.build_schema_text_from_tables")
@patch("api.routers.agents.generate_sql_candidates")
@patch("api.routers.agents.pick_best_sql")
@patch("api.routers.agents.answer_kb_question")
@patch("api.routers.agents.hybrid_synthesis")
@patch("api.routers.agents.fraud_risk_narrative")
def test_agentic_query_bypass(
    mock_fraud, mock_hybrid, mock_kb, mock_pick, mock_gen, mock_schema,
    client, auth_headers
):
    # Setup mocks for minimal bypass case
    mock_schema.return_value = "Schema Context"
    mock_gen.return_value = ["SELECT 1"]
    
    mock_df = pd.DataFrame([{"result": 1}])
    mock_pick.return_value = {
        "best": {"sql": "SELECT 1", "df": mock_df, "error": None},
        "all_candidates": []
    }
    
    response = client.post(
        "/agents/query",
        json={
            "question": "Test question",
            "bypass_agents": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sql"] == "SELECT 1"
    assert data["explanation"] == "Skipped (Bypass Mode)"
    assert data["synthesis"] == "Skipped (Bypass Mode)"

@patch("api.routers.agents.build_schema_text_from_tables")
@patch("api.routers.agents.generate_sql_candidates")
@patch("api.routers.agents.pick_best_sql")
@patch("api.routers.agents.explain_join_query")
@patch("api.routers.agents.reconcile_sql_results")
@patch("api.routers.agents.answer_kb_question")
@patch("api.routers.agents.hybrid_synthesis")
@patch("api.routers.agents.fraud_risk_narrative")
def test_agentic_query_full_pipeline(
    mock_fraud, mock_hybrid, mock_kb, mock_recon, mock_explain, mock_pick, mock_gen, mock_schema,
    client, auth_headers
):
    # Setup mocks for full pipeline
    mock_schema.return_value = "Full Schema"
    mock_gen.return_value = ["SELECT * FROM t"]
    
    mock_df = pd.DataFrame([{"id": 1, "fraud": 0}])
    mock_pick.return_value = {
        "best": {"sql": "SELECT * FROM t", "df": mock_df, "error": None},
        "all_candidates": []
    }
    
    mock_explain.return_value = "This query explains..."
    mock_recon.return_value = "Reconciled results..."
    mock_kb.return_value = {"contexts": ["Context A"]}
    mock_hybrid.return_value = "Synthesized answer..."
    mock_fraud.return_value = "Fraud report..."
    
    response = client.post(
        "/agents/query",
        json={
            "question": "Full investigation",
            "bypass_agents": False
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["explanation"] == "This query explains..."
    assert data["synthesis"] == "Synthesized answer..."
    assert data["fraud_risk_report"] == "Fraud report..."
