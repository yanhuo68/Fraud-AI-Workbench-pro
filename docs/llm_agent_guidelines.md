# LLM Agent Guidelines for Fraud Analytics

This document defines how LLM agents should behave when analyzing transactions, generating SQL queries, or explaining fraud risk. The goal is consistent, safe, and accurate agent behavior.

---

# 1. Agent Objectives

Every LLM agent must:
1. Provide accurate and verifiable reasoning.
2. Avoid hallucinating fields or table names.
3. Use SQL patterns defined in `fraud_sql_patterns.md`.
4. Refer to fraud rules in `fraud_risk_rules.md`.
5. Provide explanations that follow `business_explanation_templates.md`.

---

# 2. Required Behaviors

## AG-1: Cite Rules When Explaining Results
Example:  
“This violates Rule B-1: Ledger inconsistency.”

## AG-2: Answer Only with Supported Columns
Allowed columns are defined in `database_schema_reference.md`.

## AG-3: If data is insufficient, state it clearly
Example:  
“The dataset does not contain geographic information, so I cannot evaluate geographic anomalies.”

## AG-4: Do not invent statistical models
Use:
- Isolation Forest  
- Random Forest  
- Balance checks  
- SQL patterns provided  

---

# 3. SQL Safety Guidelines

## AG-SQL-1: Always validate the query against schema.
## AG-SQL-2: Avoid unsupported SQL functions.
## AG-SQL-3: Use `LIMIT` for large result sets.
## AG-SQL-4: Avoid CROSS JOIN unless necessary.

---

# 4. Explanation Guidelines

Explanations should:
- Use atomic sentences.
- Reference fraud patterns.
- Provide clear risk assessments.
- Give actionable recommendations.

---

# 5. Purpose of This Document
This ensures agent consistency, safety, and accuracy in all fraud analysis tasks.
