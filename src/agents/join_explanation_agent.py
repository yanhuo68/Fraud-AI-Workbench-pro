# agents/join_explanation_agent.py

"""
JOIN Explanation Agent

Takes:
- User question
- Best SQL
- Result table
- ERD / schema info

Returns:
- Plain English explanation
- Why JOIN was needed
- Logic behind relationships
"""

from agents.llm_router import init_llm
import pandas as pd

def explain_join_query(
    question: str,
    sql: str,
    df: pd.DataFrame,
    schema_text: str,
    llm_id: str,
) -> str:

    llm = init_llm(llm_id)

    table_preview = df.to_markdown(index=False) if df is not None and len(df) > 0 else "EMPTY_RESULT"

    prompt = f"""
You are a senior data engineer and SQL expert.

The user asked:
{question}

The SQL query chosen was:
```sql
{sql}
The SQL returned this result (markdown table):
{table_preview}

Below is ERD + schema information for all tables:
{schema_text}

Explain:
1.Why the JOIN was required
2.Which tables and keys were joined
3.How primary key / foreign key relationships support this JOIN
4.What the result means in the context of fraud analytics
5.If result is empty, explain possible reasons

Write a clear explanation.
"""
    resp = llm.invoke(prompt)
    return resp.content