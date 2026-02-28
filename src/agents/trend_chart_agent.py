# agents/trend_chart_agent.py

"""
Automatically detect date/time columns and produce trend charts.
Also produce LLM-driven narrative insight about the trend.
"""

import pandas as pd
import altair as alt
from agents.llm_router import init_llm


def detect_datetime_column(df):
    """
    Automatic detection of time/date column.
    Returns a column name or None.
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        if any(x in col.lower() for x in ["date", "time", "timestamp", "day", "created"]):
            try:
                pd.to_datetime(df[col])
                return col
            except:
                continue
    return None


def build_trend_chart(df):
    """
    Generate an Altair line chart for the detected datetime column.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        return None, None

    date_col = detect_datetime_column(df)
    if date_col is None:
        return None, None

    # Convert to datetime
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Pick numeric columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return None, None

    # Build chart
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=date_col + ":T",
            y=numeric_cols[0] + ":Q",
            tooltip=numeric_cols + [date_col],
        )
        .interactive()
    )

    return chart, date_col


def generate_trend_insights(df: pd.DataFrame, question: str, llm_id: str, schema_text: str):
    """
    Let the LLM generate narrative about the trend.
    """
    llm = init_llm(llm_id)

    preview = df.head(20).to_markdown(index=False) if len(df) else "EMPTY"

    prompt = f"""
You are a senior fraud analyst.
We ran this SQL question:

{question}

Here is a preview of the SQL result:
{preview}

Here is the schema + ERD information:
{schema_text}

Your job:
1. Identify if a trend exists.
2. Explain the direction (increasing, decreasing, spikes, anomalies).
3. Mention possible fraud signals or risk.
4. Produce a short analytic insight summary.
"""

    return llm.invoke(prompt).content
