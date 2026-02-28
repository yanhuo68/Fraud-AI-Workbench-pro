# agents/sql_recovery_agent.py

"""
SQL Recovery Agent

Goal: When JOIN SQL fails (syntax error, no such column, etc.),
the agent uses LLM to repair the SQL based on:

- Error message
- Schema text (PK/FK, ERD, column types)
- Original user question
"""

from agents.llm_router import init_llm

def repair_sql(
    question: str,
    bad_sql: str,
    error_message: str,
    schema_text: str,
    llm_id: str,
) -> str:
    """
    Given a failing SQL query, request LLM to fix it.
    Returns new SQL OR fallback single-table SQL.
    """

    llm = init_llm(llm_id)

    prompt = f"""
You are a SQL repair expert for SQLite.

The user asked:
{question}

The SQL query below FAILED:
```sql
{bad_sql}
Error message from SQLite:
{error_message}

Here is the schema, ERD, PK/FK information for all tables:
{schema_text}

Your job:

1.Identify the reason for the failure.
2.Correct the SQL query to a valid JOIN or SELECT.
3.Use ONLY tables/columns from the schema above.
4.Prefer JOIN queries if relationships exist.
5.If JOIN is impossible, generate a simpler single-table SELECT query.
6.Return ONLY SQL with no explanation.

Begin.
"""
    repaired = llm.invoke(prompt).content.strip()
    return repaired 
    