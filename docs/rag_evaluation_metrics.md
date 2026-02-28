# RAG Evaluation Metrics for Fraud Analysis

This document defines metrics used to evaluate the accuracy and quality of Retrieval-Augmented Generation (RAG) in fraud analytics.

---

# 1. Retrieval Quality Metrics

## R1: Recall@k
% of queries where at least one relevant document is retrieved.

## R2: Precision@k
% of retrieved documents that are relevant.

## R3: Context Relevance Score
Manual evaluation whether retrieved docs match the query intent.

---

# 2. Generation Quality Metrics

## G1: Faithfulness
Does the output rely only on retrieved context?

## G2: Hallucination Rate
% of responses containing:
- Fabricated SQL fields
- Unsupported fraud rules
- Incorrect balance logic

## G3: Explanation Accuracy
Does the LLM reference valid rules from the knowledge-base?

---

# 3. End-to-End RAG Metrics

## E1: SQL Validity Rate
% of SQL queries that run successfully.

## E2: Domain Consistency
Output references:
- fraud_intro.md  
- fraud_risk_rules.md  
- model_interpretation.md  
- fraud_chain_patterns.md  

## E3: Answer Correctness
Manual or synthetic evaluation.

---

# 4. Evaluation Procedure

1. Define synthetic fraud questions.  
2. Run through RAG pipeline.  
3. Score retrieval + generation separately.  
4. Collect traces from LangGraph nodes.  
5. Use LangSmith or custom eval tools.

---

# Purpose of This Document
Provide a reliable framework for evaluating RAG performance in the fraud analytics system.
