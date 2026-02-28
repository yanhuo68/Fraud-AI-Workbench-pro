# ML Evaluation Recipes for Fraud Detection

This document defines how to evaluate models programmatically.

---

# 1. Classification Recipe
- Train RF
- Predict probabilities
- Compute:
  - Precision
  - Recall
  - F1
  - AUC
  - Confusion matrix
- Plot ROC curve
- Show feature importance

---

# 2. Isolation Forest Recipe
- Train on normal data only
- Score test data
- Normalize scores
- Compute Precision@k
- Visualize score distributions

---

# 3. LOF Recipe
- Fit LOF
- Use `negative_outlier_factor_`
- Rank transactions
- Show anomalies table

---

# 4. Threshold Optimization Recipe
Find threshold maximizing F1:
best_threshold = argmax(F1(prob >= threshold))

---

# 5. Report Generation Recipe
LLM explains:
- Model performance
- Top features
- Fraud insights
- False positive root causes
