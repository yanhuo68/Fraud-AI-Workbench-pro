import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from agents.fraud_risk_agent import add_fraud_risk_score, fraud_risk_narrative
from agents.sql_reconciliation_agent import reconcile_sql_results

def test_add_fraud_risk_score_heuristics():
    # Test case 1: High amount
    df = pd.DataFrame([
        {"amount": 10.0, "type": "PAYMENT"},
        {"amount": 1000.0, "type": "PAYMENT"},
        {"amount": 10000.0, "type": "PAYMENT"}
    ])
    scored = add_fraud_risk_score(df)
    assert "fraud_risk_score" in scored.columns
    # Row 3 (10000) should have higher risk than Row 1 (10)
    assert scored.loc[2, "fraud_risk_score"] > scored.loc[0, "fraud_risk_score"]

    # Test case 2: Risky transaction type
    df_types = pd.DataFrame([
        {"amount": 100.0, "type": "DEBIT"},
        {"amount": 100.0, "type": "CASH_OUT"}
    ])
    scored_types = add_fraud_risk_score(df_types)
    # CASH_OUT should be riskier than DEBIT for same amount
    assert scored_types.loc[1, "fraud_risk_score"] > scored_types.loc[0, "fraud_risk_score"]

    # Test case 3: Late night transaction
    df_time = pd.DataFrame([
        {"amount": 100.0, "timestamp": "2024-01-01 14:00:00"}, # Afternoon
        {"amount": 100.0, "timestamp": "2024-01-01 02:00:00"}  # 2 AM
    ])
    scored_time = add_fraud_risk_score(df_time)
    assert scored_time.loc[1, "fraud_risk_score"] > scored_time.loc[0, "fraud_risk_score"]

@patch("agents.fraud_risk_agent.init_llm")
def test_fraud_risk_narrative(mock_init_llm):
    mock_llm = MagicMock()
    mock_init_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = "Risk narrative result"
    
    df = pd.DataFrame([{"amount": 1000.0, "fraud_risk_score": 0.8}])
    narrative = fraud_risk_narrative(df, "Why is this risky?", "Schema info", "mock-llm")
    
    assert narrative == "Risk narrative result"
    mock_llm.invoke.assert_called_once()

@patch("agents.sql_reconciliation_agent.init_llm")
def test_reconcile_sql_results(mock_init_llm):
    mock_llm = MagicMock()
    mock_init_llm.return_value = mock_llm
    mock_llm.invoke.return_value.content = "Reconciliation result"
    
    candidates = [
        {"sql": "SELECT 1", "score": 0.9, "df": pd.DataFrame([{"res": 1}]), "error": None},
        {"sql": "SELECT 2", "score": 0.1, "df": None, "error": "Syntax error"}
    ]
    
    result = reconcile_sql_results("Test q", candidates, "Schema info", "mock-llm")
    
    assert result == "Reconciliation result"
    mock_llm.invoke.assert_called_once()
    # Verify that the prompt contains the candidate info
    prompt = mock_llm.invoke.call_args[0][0]
    assert "Candidate 1" in prompt
    assert "Candidate 2" in prompt
    assert "Syntax error" in prompt
