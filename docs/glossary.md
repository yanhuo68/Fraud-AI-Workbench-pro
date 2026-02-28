# Glossary of Fraud Detection Terms

This glossary defines all important terminology used in the fraud analytics system. LLMs reference this document to ensure consistent language.

---

## Fraud
Unauthorized or malicious financial activity intended to illegally gain value.

## Fraud Chain
A sequence of coordinated transactions typically used to launder or extract funds (e.g., TRANSFER → CASH_OUT).

## Money Mule
An account used to receive fraudulent funds and forward or cash them out.

## Ledger Inconsistency
Mismatch between expected and actual account balances (e.g. `oldbalanceOrg - amount != newbalanceOrig`).

## Anomaly
An unusual transaction based on statistical patterns.

## Model Drift
Degradation of ML performance due to changing behavior patterns.

## Precision
% of flagged fraud cases that are truly fraud.

## Recall
% of actual fraud cases that were successfully detected.

## AUC-ROC
Performance metric evaluating ranking ability for binary classification.

## FP (False Positive)
Normal transaction flagged as fraud.

## FN (False Negative)
Fraud transaction not detected.

## Isolation Forest
Unsupervised anomaly detection algorithm that isolates outliers.

## Random Forest
Supervised ensemble classifier for fraud detection.

## RAG (Retrieval-Augmented Generation)
LLM method combining context retrieval and generation.

---
