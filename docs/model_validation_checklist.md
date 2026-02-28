
---

# 📙 **2. docs/model_validation_checklist.md**

```markdown
# Model Validation Checklist for Fraud Detection

This checklist provides a structured method for evaluating the performance, fairness, and operational quality of fraud detection models (Isolation Forest, Random Forest, and others).

LLMs should use this checklist when critiquing model outputs.

---

# 1. Data Quality Validation

## DQ-1: Missing Values
Check if any feature contains missing or invalid values.

## DQ-2: Class Imbalance
Evaluate:
- Ratio of `isFraud = 1` vs `isFraud = 0`
- Need for resampling or class weights.

## DQ-3: Data Leakage
Ensure no target information leaks into features.

---

# 2. Model Performance Validation

## MP-1: Precision and Recall for Fraud Class
- Precision (fraud) should not be too low (avoid false alarms).
- Recall (fraud) should be as high as possible (catch fraud).

## MP-2: AUC-ROC
AUC > 0.90 indicates strong model performance.

## MP-3: False Negative Rate
Key metric:
FN / (FN + TP)

---

# 3. Interpretability Validation

## INT-1: Feature Importance Stability
Check if important features match known fraud patterns:
- `amount`
- Balance inconsistencies
- Transfer → cash-out patterns

## INT-2: Anomaly Score Reasoning (Isolation Forest)
Ensure anomalies map to:
- High amounts
- Inconsistent balances
- Unusual sender behavior

---

# 4. Operational Safety Checks

## OS-1: Threshold Calibration
Threshold must balance FN and FP trade-offs.

## OS-2: Drift Monitoring
Models degrade over time; monitor:
- Fraud patterns
- Amount distributions
- Transaction types

## OS-3: Human-in-the-loop Feasibility
Fraud teams must be able to:
- Review flagged transactions
- Validate scores
- Interpret explanations

---

# 5. SQL Integration Validation

## SQL-1: Query Consistency
SQL queries should follow patterns defined in `fraud_sql_patterns.md`.

## SQL-2: Aggregation Validation
Check if sums, averages, and counts match expected dataset behavior.

---

# Purpose of This Document
This checklist improves:
- LLM explanations for model results
- Model critique accuracy
- Operational reliability of fraud detection workflows
