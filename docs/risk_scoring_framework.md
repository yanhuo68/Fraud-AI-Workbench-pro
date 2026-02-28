# Risk Scoring Framework for Fraud Detection

This document defines a unified scoring framework used to compute risk levels for transactions. ML models, SQL queries, LLM explanations, and RAG all refer to this document for consistency.

---

# 1. Risk Score Components

Risk score (0–100) is composed of:

1. **Anomaly Score Weight (30%)**
2. **Model Fraud Probability Weight (40%)**
3. **Rule Violations Weight (20%)**
4. **Fraud Chain Indicators Weight (10%)**

Each component is normalized to ensure consistent final scores.

---

# 2. Anomaly Score Component (30%)

`anomaly_score_normalized × 30`

Normalization:
normalized = (score - min) / (max - min)

---

# 3. Fraud Probability Component (40%)

`fraud_probability × 40`

When RF probability > 0.9, strong fraud signal.

---

# 4. Rule Violations (20%)

Each violated rule adds weighted penalties:

| Rule | Weight |
|------|--------|
| Ledger error (B-1/B-2) | +10 |
| Zero-balance manipulation | +5 |
| New destination | +3 |
| Amount spike | +5 |
| Velocity anomaly | +5 |

Maximum = 20 points.

---

# 5. Fraud Chain Indicator (10%)

+10 if transaction matches any pattern in `fraud_chain_patterns.md`  
Else 0.

---

# 6. Final Risk Score
risk_score = anomaly_component
+ probability_component
+ rule_component
+ chain_component

Range: **0–100**

---

# 7. Interpretation

| Score Range | Meaning |
|-------------|---------|
| 0–40 | Low risk |
| 41–70 | Medium risk |
| 71–100 | High risk |

---

# Purpose of This Document
This framework ensures:
- Unified scoring across models
- Consistent alert severity
- Reliable LLM-driven risk assessments

