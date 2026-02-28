# agents/sql_improvement_agent.py

"""
Suggest improvements to a SQL query:
- Better JOIN logic
- More efficient filtering
- Aggregations
- Index recommendations
- Data quality suggestions
"""

from agents.llm_router import init_llm

def suggest_sql_improvements(question, sql, schema_text, llm_id):
    llm = init_llm(llm_id)

    prompt = f"""
You are a senior SQL engineer and optimizer.

The user asked:
{question}

Here is the SQL we executed:
```sql
{sql}

Here is the schema and ERD information:
{schema_text}

Your tasks:
1.Suggest improvements to:
  - JOIN logic
  - Filtering conditions
  - Performance
  - Grouping & aggregations
  - Window functions
2.Suggest any indexes that might improve performance.
3.Suggest alternative SQL formulations.
4.DO NOT write code unless necessary — mostly explanations.

Produce a helpful improvement review.
"""
    return llm.invoke(prompt).content
    