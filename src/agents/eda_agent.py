# agents/eda_agent.py

"""
EDA Agent

- Computes basic EDA summaries on a SQL result DataFrame
- Numeric stats (min, max, mean, std)
- Categorical value counts (top categories)
- LLM narrative summary
"""

import pandas as pd
from agents.llm_router import init_llm


def compute_basic_eda(df: pd.DataFrame) -> dict:
    """
    Return a dict with:
    - numeric_summary: df.describe() for numeric cols
    - categorical_summary: top categories for object/string cols
    """
    result = {}

    if df is None or df.empty:
        return {"numeric_summary": None, "categorical_summary": None}

    num_df = df.select_dtypes(include="number")
    cat_df = df.select_dtypes(exclude="number")

    numeric_summary = num_df.describe().T if not num_df.empty else None

    categorical_summary = {}
    if not cat_df.empty:
        for col in cat_df.columns:
            vc = cat_df[col].value_counts().head(10)
            categorical_summary[col] = vc

    result["numeric_summary"] = numeric_summary
    result["categorical_summary"] = categorical_summary

    return result


def eda_narrative(
    df: pd.DataFrame,
    question: str,
    eda_summary: dict,
    schema_text: str,
    llm_id: str,
) -> str:
    """
    Use LLM to generate a narrative based on EDA results.
    """

    llm = init_llm(llm_id)

    if df is None or df.empty:
        preview = "EMPTY_RESULT"
    else:
        preview = df.head(20).to_markdown(index=False)

    numeric_text = ""
    if eda_summary.get("numeric_summary") is not None:
        numeric_text = eda_summary["numeric_summary"].to_markdown()

    categorical_text = ""
    cat_sum = eda_summary.get("categorical_summary") or {}
    for col, vc in cat_sum.items():
        categorical_text += f"\nColumn `{col}` top categories:\n{vc.to_markdown()}\n"

    prompt = f"""
You are a senior data scientist performing EDA for fraud analytics.

User question:
{question}

Sample of SQL result (first rows):
{preview}

Numeric summary (per numeric column):
{numeric_text}

Categorical summary (top categories per column):
{categorical_text}

Schema and ERD info:
{schema_text}

Your tasks:
1. Describe the main distribution characteristics (ranges, skewness, outliers hints).
2. Highlight columns that are likely important for fraud analysis.
3. Suggest what additional analysis might be useful next.

Write a concise EDA summary.
"""

    return llm.invoke(prompt).content
