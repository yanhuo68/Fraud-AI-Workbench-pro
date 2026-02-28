# Test Cases Suite for Fraud Analytics System

This document defines synthetic and real-world inspired test cases to validate the ML models, SQL queries, and agent reasoning.

---

# 1. SQL Test Cases

## TC-SQL-1: Fraud Count
Question: "How many fraud transactions exist?"

## TC-SQL-2: Largest Transactions
"Show the top 10 largest fraud transactions."

## TC-SQL-3: Ledger Inconsistency Detection
"Find transactions where sender balance does not match ledgers."

---

# 2. ML Model Test Cases

## TC-ML-1: Class Imbalance Detection
Dataset should have <1% fraud.

## TC-ML-2: Isolation Forest Sanity Check
IF score must detect:
- High amounts  
- Ledger inconsistencies  

## TC-ML-3: Random Forest Performance
AUC must be > 0.9 on default dataset.

---

# 3. LLM Explanation Test Cases

## TC-LLM-1: Explain High Anomaly Score
Should cite:
- Amount spike
- Balance anomaly

## TC-LLM-2: Explain False Negative
Should identify:
- Mimicked normal behavior

---

# 4. Knowledge-Base RAG Test Cases

## TC-RAG-1: Which fraud patterns exist?
Should reference fraud_chain_patterns.md.

## TC-RAG-2: Explain ledger inconsistencies
Should reference fraud_risk_rules.md.

---
