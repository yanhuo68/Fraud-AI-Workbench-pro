# Fraud Detection Measurement Framework

Each file defines:
- Core fraud KPIs
- Model performance metrics
- Operational efficiency metrics
- Financial impact metrics
- Monitoring indicators

---

## Measurement Categories

1. Model Performance
2. Financial Impact
3. Operational Efficiency
4. Customer Impact
5. Risk & Compliance

# Common Fraud Detection Metrics (All Industries)

## 1. Classification Metrics

### Precision
Precision = True Positives / (True Positives + False Positives)

Measures how many flagged cases are actually fraud.

### Recall (Detection Rate)
Recall = True Positives / (True Positives + False Negatives)

Measures how much fraud is successfully detected.

### F1 Score
Harmonic mean of Precision and Recall.

### False Positive Rate (FPR)
False Positives / Legitimate Transactions

Critical for customer experience.

### False Negative Rate (FNR)
Missed Fraud / Total Fraud

High business risk if elevated.

### ROC-AUC
Area Under ROC Curve – model ranking capability.

### PR-AUC
Precision-Recall AUC – more suitable for imbalanced fraud datasets.

---

## 2. Financial Metrics

### Fraud Rate
Fraud Cases / Total Volume

### Fraud Loss Rate
Fraud Loss / Total Transaction Value

### Net Fraud Loss
Fraud Loss – Recoveries

### Cost Per Investigation
Operational cost per reviewed case.

### Return on Fraud Prevention
(Fraud Prevented – Cost of Controls) / Cost of Controls
