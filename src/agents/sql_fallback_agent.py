"""
Fallback query generator for cases where JOIN SQL and recovery both fail.
"""

from agents.llm_router import init_llm

def generate_fallback_sql(question: str, table: str, schema_text: str, llm_id: str) -> str:
    """
    Generate a simple SQL query for a single table.
    """
    llm = init_llm(llm_id)

    prompt = f"""
The user asked:
{question}

JOIN queries did not work for this question.

You must now generate a simple SQLite query against ONE table only:
- Table: {table}
- Use only its columns from the schema below:

Schema:
{schema_text}

Rules:
- No JOIN
- Must be valid SQLite
- Only SELECT queries
- Return ONLY SQL code
"""

    return llm.invoke(prompt).content.strip()