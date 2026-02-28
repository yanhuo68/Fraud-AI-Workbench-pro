# agents/sql_ranking_agent.py

"""
JOIN SQL Ranking Agent

Responsible for:
- Generating multiple JOIN SQL candidates
- Executing each candidate safely
- Scoring each result
- Selecting the best SQL
"""

from typing import List, Dict, Tuple
import pandas as pd
from agents.llm_router import init_llm
from rag_sql.sql_utils import run_sql_query


# -----------------------------------------------------
# 1. Generate Multiple JOIN SQL candidates
# -----------------------------------------------------
def generate_sql_candidates(question: str, llm_id: str, schema_text: str, k: int = 3) -> List[str]:
    """
    Generate multiple JOIN SQL queries using LLM.
    """

    llm = init_llm(llm_id)

    prompt = f"""
You are an expert SQL generator. The user asked:

{question}

You MUST obey these rules:
- CRITICAL: Use ONLY the exact tables and columns provided in the schema below. 
- CRITICAL: DO NOT hallucinate or invent tables like 'Orders', 'Products', 'Transactions', 'Users' unless they explicitly appear in the schema.
- JOIN RULES: ONLY use JOINs if the schema lists "Explicit Relationships (Foreign Keys)" OR if two tables share an identical ID column name. If the schema says "Explicit Relationships: NONE", do NOT attempt to join it with other tables to answer the query; query it individually.
- Produce SQLite-compatible SQL.
- Return ONLY SQL queries with no commentary.
- Generate {k} DIFFERENT valid SQL queries.

Schema and ERD information:
{schema_text}

Return queries separated by:

===ENDSQL===
"""

    resp = llm.invoke(prompt).content.strip()

    # split into separate SQL queries
    candidates = [x.strip() for x in resp.split("===ENDSQL===") if x.strip()]
    return candidates[:k]


# -----------------------------------------------------
# 2. Execute and Score SQL candidates
# -----------------------------------------------------
def score_sql_candidate(sql: str) -> Tuple[float, pd.DataFrame, str]:
    """
    Execute SQL and score result on:
    - Non-emptiness (best)
    - More rows = slightly better
    - Wider columns = slightly better
    """

    try:
        df, cols = run_sql_query(sql)
    except Exception as e:
        return -1.0, None, str(e)

    if df is None:
        return -1.0, None, "No result"

    # scoring:
    # non-empty -> +10
    score = 0
    if len(df) > 0:
        score += 10
        score += min(len(df), 50) / 5   # up to +10
        score += min(len(cols), 20) / 10  # up to +2
    else:
        score = 0

    return score, df, None


# -----------------------------------------------------
# 3. Rank all candidates and pick best
# -----------------------------------------------------
def pick_best_sql(candidates: List[str]) -> Dict:
    results = []

    for sql in candidates:
        score, df, error = score_sql_candidate(sql)
        results.append({
            "sql": sql,
            "score": score,
            "df": df,
            "error": error,
        })

    # sort by score descending
    best = sorted(results, key=lambda x: x["score"], reverse=True)[0]

    return {
        "best": best,
        "all_candidates": results,
    }
