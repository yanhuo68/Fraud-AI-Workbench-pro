# User Intent Interpretation Guide for Fraud Analytics

This guide helps the LLM interpret ambiguous user questions and convert them into accurate SQL queries or explanations.

---

# 1. User Question Types

## Q-1: Summary Questions
Examples:
- “How many fraud cases occurred?”
- “What percentage of transactions are suspicious?”

LLM should generate **aggregation SQL**.

---

## Q-2: Exploratory Questions
Examples:
- “Show me unusual transactions.”
- “Which accounts look suspicious?”

LLM should:
- Use anomaly detection
- Query balance inconsistencies
- Identify risky accounts

---

## Q-3: Pattern Questions
Examples:
- “Are there fraud chains?”
- “Did money move between mule accounts?”

LLM should:
- Use joins (TRANSFER → CASH_OUT)
- Reference `fraud_chain_patterns.md`

---

## Q-4: Transaction Lookup
Examples:
- “Show the largest transactions.”
- “List recent transfers.”

LLM should generate:
```sql
ORDER BY amount DESC
or
ORDER BY step DESC

## Q-5: Model Interpretation Questions
Examples:
“Why did IF flag this transaction?”
“Why is this predicted as fraud?”

LLM should reference:
model_interpretation.md
fraud_risk_rules.md

# 2. Clarifying Ambiguous Questions
LLM should ask clarifying questions if:
User doesn’t specify transaction range
User doesn’t specify sender vs destination
Query asks for impossible data (e.g., timestamps not present)

# 3. Avoiding SQL Errors
LLM should:
Use the exact table name transactions
Only use existing fields
Avoid joins on non-existent columns
Avoid aggregate column hallucination

Purpose of This Document
This guide ensures:
Stable SQL generation
Accurate interpretation of user goals
Reduction of hallucinations or invalid queries
