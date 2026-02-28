# Agent Flowcharts for Fraud Detection System

This document describes the operational workflows for the LangGraph multi-agent system used in fraud analytics. Each step is atomic to ensure compatibility with RAG and LLM reasoning.

---

# 1. SQL RAG Agent Flow

Flowchart (text-based):

1. **User Question → Natural Language Input**
2. **SQL Planner Agent**
   - Parses user intent.
   - Generates SQL following `fraud_sql_patterns.md`.
3. **SQL Executor**
   - Executes SQL on `transactions` table.
   - Returns rows or error.
4. **Critic Agent**
   - Validates SQL correctness.
   - Detects missing rules.
   - Explains results using:
     - `fraud_intro.md`
     - `fraud_risk_rules.md`
     - `fraud_chain_patterns.md`
5. **UI Output**
   - Display SQL
   - Display results
   - Display critique

---

# 2. Fraud Knowledge-Base Agent Flow

1. **User Question → NL Query**
2. **Retriever**
   - Retrieves documents from:
     - `fraud_intro.md`
     - `fraud_risk_rules.md`
     - `fraud_chain_patterns.md`
     - `feature_engineering_guide.md`
3. **LLM Generator**
   - Answers using only retrieved context.
4. **Hallucination Guard**
   - Rejects unsupported fields.
   - Rejects unsupported fraud rules.

---

# 3. Model Interpretation Agent Flow

1. **Model Output**
   - Anomaly scores
   - Probabilities
2. **Model Explanation Agent**
   - Maps scores to rules in:
     - `model_interpretation.md`
     - `business_explanation_templates.md`
3. **Explainability Layer**
   - Provides reasoning in clear business terms.
4. **UI Summary**

---

# 4. Fraud Chain Detection Flow

1. Identify `TRANSFER` transactions.
2. For each:
   - Look for matching `CASH_OUT` in step+1.
3. Validate ledger transitions.
4. Generate chain structure.
5. Provide explanation based on:
   - `fraud_chain_patterns.md`
   - `fraud_risk_rules.md`

---

# Purpose of This Document
These flowcharts give LLM agents a reference structure to keep output predictable, interpretable, and aligned with the intended system behavior.
