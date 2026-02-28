# agents/sql_reconciliation_agent.py

"""
SQL Reconciliation Agent

Given:
- Multiple SQL candidates
- Their results
- Their error messages

The agent:
- Compares results
- Detects inconsistencies
- Merges insights
- Chooses best aligned result
- Explains differences

This is used AFTER the Ranking Agent and Recovery Agent.
"""

from agents.llm_router import init_llm
import pandas as pd


def reconcile_sql_results(
    question: str,
    candidate_records: list,
    schema_text: str,
    llm_id: str,
) -> str:
    """
    candidate_records = [
      {
        "sql": "...",
        "score": float,
        "df": DataFrame or None,
        "error": error_message or None
      },
      ...
    ]
    """

    llm = init_llm(llm_id)

    # Build comparison table
    table_summaries = []
    for i, rec in enumerate(candidate_records):
        if rec["df"] is None or len(rec["df"]) == 0:
            preview = "EMPTY_RESULT"
        else:
            preview = rec["df"].head().to_markdown(index=False)

        table_summaries.append(
            f"### Candidate {i+1}\n"
            f"SQL:\n```sql\n{rec['sql']}\n```\n"
            f"Score: {rec['score']}\n"
            f"Error: {rec['error']}\n"
            f"Preview:\n{preview}\n"
        )

    comparison_text = "\n\n".join(table_summaries)

    prompt = f"""
You are a SQL reconciliation analyst. Multiple SQL queries were generated for:

User question:
{question}

Based on the full schema and ERD:
{schema_text}

Here are all SQL candidates with errors, results, and previews:
{comparison_text}

Your tasks:
1. Compare the SQL queries and identify discrepancies.
2. Explain why their results differ.
3. Identify which candidate(s) are correct or partially correct.
4. If possible, synthesize a unified interpretation that uses the most reliable information.
5. Provide a concise and accurate summary of the final analytic insight.

Write the final answer as a clear explanation.
"""

    response = llm.invoke(prompt)
    return response.content
