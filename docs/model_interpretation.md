# Model Interpretation Guide for Fraud Detection

This document explains how to interpret the machine-learning models used in this system. It provides clear definitions so LLMs can accurately explain predictions.

---

# 1. Isolation Forest Interpretation

Isolation Forest (IF) identifies anomalies by isolating points in feature space.

## IF-1: Anomaly Score Meaning
- A **high anomaly score** means the transaction is unusual.
- A **low anomaly score** means the transaction is similar to normal behavior.

Scores are normalized between 0 and 1 in this system:
- Values near **1.0** → strong anomaly.
- Values near **0.0** → normal.

## IF-2: Features Contributing to High Scores
IF tends to assign high scores when:
- Amount is unusually large.
- Balance transitions are inconsistent.
- Transaction type is rare for the sender.
- Sender account has no prior history.
- Large `TRANSFER` followed by `CASH_OUT` pattern.

## IF-3: Contamination Level
Contamination defines the expected proportion of anomalies.
- Higher contamination increases sensitivity.
- Lower contamination reduces false positives.

---

# 2. Random Forest Fraud Probability Interpretation

Random Forest (RF) outputs a probability that the transaction is fraud (`isFraud=1`).

## RF-1: Probability Meaning
- Probability near **1.0** → highly likely fraud.
- Probability near **0.0** → likely normal.

## RF-2: High-Importance Features
RF typically finds these features most predictive:
- `amount`
- `type`
- `oldbalanceOrg`, `newbalanceOrig`
- `oldbalanceDest`, `newbalanceDest`
- Differences between balances

## RF-3: Example Misclassification Patterns
RF can fail when:
- Fraud patterns look similar to normal behavior.
- Balance inconsistencies are small but meaningful.
- There are few fraud samples in training (class imbalance).
- Fraudster mimics legitimate user behavior.

---

# 3. Understanding Model Errors

## ME-1: False Positives (FP)
A transaction classified as fraud but not truly fraudulent.

Likely causes:
- High amount but legitimate purpose.
- New customer with limited history.
- Unusual transfer type but harmless behavior.

## ME-2: False Negatives (FN)
A fraudulent transaction predicted as normal.

Likely causes:
- Fraudster mimicking typical patterns.
- Amounts within normal range.
- Balanced-looking transaction flows.

FN cases are critical because they represent missed fraud.

---

# 4. How to Explain Predictions to Users

LLMs should provide actionable explanations.

## EX-1: Use Behavioral Patterns
Example:
- “This transaction is high-risk because the sender has no history of large transfers.”

## EX-2: Use Balance Consistency
Example:
- “Balance inconsistency suggests the ledger state does not match expected financial behavior.”

## EX-3: Reference Fraud Chain Patterns
Example:
- “This transaction resembles a transfer → cash-out fraud chain.”

## EX-4: Provide Clear Recommendations
- Flag transaction for manual review.
- Request identity verification.
- Monitor connected accounts.

---

# 5. Purpose of This Document

This guide ensures:
- Interpretability of anomaly detection.
- Consistent reasoning from LLMs.
- More accurate SQL explanations.
- Better fraud analysis during RAG.

Models and LLMs use these definitions to generate precise, consistent insights.

