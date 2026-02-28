# Model Retraining Policy for Fraud Detection

This document specifies when and how fraud detection models must be retrained.

---

# 1. Retraining Triggers

## R1: Performance Degradation
- AUC drops >5%
- FN rate increases >10%

## R2: Dataset Drift
- Amount distributions shift
- New fraud chains appear

## R3: Rule-Based Drift
- Increase in rule violations

---

# 2. Retraining Frequency

Minimum schedule:
- Monthly retraining for production-like systems
- Weekly retraining for adversarial environments

---

# 3. Retraining Dataset Requirements

Dataset must include:
- Recent samples
- Updated fraud patterns
- Balanced training subsets

---

# 4. Retraining Validation

Validation must include:
- AUC  
- Precision/Recall  
- Confusion Matrix  
- Feature importance stability  
- Model interpretation stability  

---

# 5. Deployment Checklist

Before deployment:
- Drift check
- Bias inspection
- Explainability test
- SQL consistency validation

---
