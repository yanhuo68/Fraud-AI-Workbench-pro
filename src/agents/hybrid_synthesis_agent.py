# agents/hybrid_synthesis_agent.py

"""
Hybrid SQL + RAG Synthesis Agent

Combines:
- SQL result DataFrame
- Schema information
- Relevant RAG context documents
- Fraud domain knowledge

Produces:
- A narrative analytic report
"""

from agents.llm_router import init_llm

def hybrid_synthesis(
    question: str,
    sql: str,
    df,
    rag_contexts: list,
    schema_text: str,
    llm_id: str,
) -> str:

    llm = init_llm(llm_id)

    # SQL result preview
    if df is None or len(df) == 0:
        sql_preview = "EMPTY_RESULT"
    else:
        sql_preview = df.to_markdown(index=False)

    # Build RAG context text
    rag_text = ""
    for i, ctx in enumerate(rag_contexts):
        rag_text += (
            f"\n### Context {i+1} (Source: {ctx['metadata'].get('source','unknown')})\n"
            f"{ctx['content']}\n"
        )

    prompt = f"""
You are a senior fraud analytics expert.

You must synthesize the final answer from BOTH:

1. SQL result:
```sql
{sql}
Result preview:
{sql_preview}

RAG contexts (retrieved fraud rules, schema, business logic):
{rag_text}

Table schemas and ERD metadata:
{schema_text}

User question:
{question}

Your tasks:

Explain what the SQL result means.

Use retrieved RAG context to add domain knowledge: fraud patterns, risk factors, rules.

Combine SQL insights with unstructured text insights into a unified analytic report.

If SQL result is empty, rely more on RAG context to answer.

Keep the explanation precise and professional.

Write a polished final answer.
"""
    return llm.invoke(prompt).content

