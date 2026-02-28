# agents/fraud_risk_agent.py

"""
Fraud Risk Scorer

Adds a 'fraud_risk_score' column to the SQL result using simple heuristics:
- Amount magnitude
- Transaction type category (if present)
- Time-of-day (if present)
"""

import pandas as pd
from agents.llm_router import init_llm


def add_fraud_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a copy of df with an extra column 'fraud_risk_score' in [0, 1].
    """

    if df is None or df.empty:
        return df

    df2 = df.copy()

    # Base score 0
    df2["fraud_risk_score"] = 0.0

    # Amount-based risk if 'amount' column exists
    if "amount" in df2.columns:
        amt = df2["amount"].astype(float)
        # Normalize by quantiles
        q90 = amt.quantile(0.9)
        q99 = amt.quantile(0.99)
        df2["fraud_risk_score"] += (amt / (q90 + 1e-9)).clip(0, 1) * 0.4
        df2.loc[amt >= q99, "fraud_risk_score"] += 0.2  # very high values

    # Transaction type if present
    type_col = None
    for cand in ["type", "transaction_type", "txn_type"]:
        if cand in df2.columns:
            type_col = cand
            break

    if type_col is not None:
        risky_types = ["CASH_OUT", "TRANSFER", "CASHOUT", "PAYMENT_REVERSAL"]
        df2[type_col] = df2[type_col].astype(str).str.upper()
        df2.loc[df2[type_col].isin(risky_types), "fraud_risk_score"] += 0.2

    # Time-based risk (if timestamp-like)
    time_col = None
    for cand in ["timestamp", "time", "date"]:
        if cand in df2.columns:
            time_col = cand
            break

    if time_col is not None:
        # attempt parsing
        ts = pd.to_datetime(df2[time_col], errors="coerce")
        hours = ts.dt.hour
        df2["fraud_risk_score"] += (
            ((hours >= 0) & (hours <= 5)).fillna(False).astype(int) * 0.2
        )  # late night

    # Clip to [0, 1]
    df2["fraud_risk_score"] = df2["fraud_risk_score"].clip(0, 1)

    return df2


def fraud_risk_narrative(
    df: pd.DataFrame,
    question: str,
    schema_text: str,
    llm_id: str,
) -> str:
    """
    Let LLM describe risk scoring pattern and how to interpret it.
    """

    llm = init_llm(llm_id)

    if df is None or df.empty or "fraud_risk_score" not in df.columns:
        preview = "NO_RISK_SCORES_AVAILABLE"
    else:
        preview = df[["fraud_risk_score"] + [c for c in df.columns if c != "fraud_risk_score"]].head(20).to_markdown(index=False)

    prompt = f"""
You are a fraud risk analyst.

We computed a heuristic 'fraud_risk_score' between 0 and 1 for each row of the SQL result.

User question:
{question}

Sample rows with fraud_risk_score:
{preview}

Schema and ERD:
{schema_text}

Tasks:
1. Explain how to interpret the fraud_risk_score.
2. Indicate what ranges (e.g., >0.7) might be considered high risk.
3. Point out any obvious patterns between transaction attributes and high risk.
4. Suggest how this heuristic could be improved (e.g., ML model, more features).

Provide a concise explanation.
"""

    return llm.invoke(prompt).content
