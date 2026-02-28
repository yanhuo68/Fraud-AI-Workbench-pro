# ML Evaluation Metrics for Fraud Detection Models

This document defines metrics calculated in the Streamlit dashboard for uploaded datasets and trained ML models.

---

# 1. Classification Metrics (Supervised Models)

## 1.1 Accuracy
Not reliable for fraud (due to imbalance).

## 1.2 Precision (Fraud)
`TP / (TP + FP)`

## 1.3 Recall (Fraud)
`TP / (TP + FN)`  
Most important fraud metric.

## 1.4 F1 Score
Harmonic mean of precision/recall.

## 1.5 ROC-AUC
Measures ranking quality.

---

# 2. Confusion Matrix

|          | Pred 0 | Pred 1 |
|----------|--------|--------|
| True 0   | TN     | FP     |
| True 1   | FN     | TP     |

Important for:
- Explaining false positives
- Explaining false negatives

---

# 3. Anomaly Metrics (Unsupervised)

## 3.1 Anomaly Score
Normalized [0–1].

## 3.2 Precision@k for anomalies
% of top k anomalies that are fraud.

## 3.3 Outlier Ratio
How many anomalies model detects relative to expected.

---

# 4. Dataset Metrics

## 4.1 Fraud Rate
Percentage of `isFraud=1`.

## 4.2 Amount Distribution
Mean, median, 99th percentile.

## 4.3 Transaction Type Distribution
Useful for evaluating user-uploaded datasets.

---

# 5. Model Stability Metrics

## 5.1 Feature Importance Stability
Check ranking consistency.

## 5.2 Drift Indicators
Compare new dataset stats vs baseline.

---

# Purpose of This Document
This ensures LLM, UI, and models use consistent metric definitions when evaluating user-uploaded datasets.
