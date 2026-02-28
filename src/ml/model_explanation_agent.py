# agents/model_explanation_agent.py

from agents.llm_router import init_llm
import pandas as pd

def explain_model_prediction(
    df_row: pd.Series,
    probability: float,
    model_name: str,
    llm_id: str,
    schema_text: str,
):
    llm = init_llm(llm_id)

    row_text = df_row.to_markdown()

    prompt = f"""
You are a senior fraud analyst.

A machine learning model ({model_name}) scored the following transaction:

{row_text}

Predicted fraud probability: {probability:.4f}

Given the schema/ERD:
{schema_text}

Explain:
1. What likely contributes to the risk.
2. Which fields should be examined.
3. What next steps should an investigator take.
4. Whether manual review is recommended.

Make the explanation concise and useful.
"""

    return llm.invoke(prompt).content
