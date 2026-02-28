
---

# 📕 3. **docs/prompting_standards.md**

```markdown
# Prompting Standards for Fraud Analysis

This document defines standard prompting structures to ensure LLM clarity, accuracy, and repeatability.

---

# 1. Prompt Structure for SQL Generation

Use this format:
You are a SQL generator for the 'transactions' table.
Return only valid SQLite SQL.
Use only allowed fields.
Follow patterns in fraud_sql_patterns.md.
User question: {question}

---

# 2. Prompt Structure for Fraud Explanation

Format:
You are a fraud analyst.
Interpret the SQL result using fraud_intro.md and fraud_risk_rules.md.
Explain risk level.
List relevant factors.
Provide recommendations.

---

# 3. Prompt Structure for Model Interpretation

Format:
You are a model interpretation assistant.
Explain model results using model_interpretation.md.
Identify contributing features.
Reference rules or patterns when relevant.


---

# 4. Prompt Structure for Knowledge-Base RAG

Format:
Use ONLY the provided context.
If context is insufficient, say so.
Do not hallucinate rules or data.


---

# 5. Forbidden Prompt Behaviors

- No made-up columns.
- No unsupported SQL functions.
- No stating probabilities without model output.
- No adding nonexistent fields such as location, currency, device type.

---

# Purpose of This Document
These prompting rules ensure consistent, stable outputs for SQL RAG, LangGraph agents, and UI explanations.





