# Anomaly Scenarios for Fraud Detection Models

This document describes common anomaly scenarios relevant to Isolation Forest and unsupervised detection.

---

# Scenario A: Large Amount Outliers
Unusual high-value transactions relative to sender history.

Indicators:
- Amount > 99th percentile.
- Sender has no prior large payments.

---

# Scenario B: Negative Balance or Ledger Conflict
Balances do not follow expected financial logic.

Examples:
oldbalanceOrg - amount != newbalanceOrig
oldbalanceDest + amount != newbalanceDest

---

# Scenario C: New Destination High-Risk Transfer
Sender transfers to a destination account that has never appeared before.

---

# Scenario D: Timing Anomalies
Unusual timing patterns:
- Activity at abnormal hours.
- Rapid burst of transactions.

---

# Scenario E: Rare Transaction Type
Sender engages in a transaction type they have never used before.

---

# Scenario F: Combined Anomaly (Multi-Factor)
Combination of:
- High amount
- Unusual time
- New destination
- Inconsistent ledger

This is high-risk even if no fraud is labeled.

---

# Purpose of This Document
These scenarios guide:
- Isolation Forest anomaly interpretation
- LLM explanations
- SQL filtering for risk analysis
