# Feature Engineering Guide for Fraud Detection

This document defines recommended transformations and derived features for machine-learning models used in fraud detection. All features are written in a clear and consistent way to support RAG and LLM-based model interpretation.

---

# 1. Amount-Based Features

## F1: Normalized Amount
`amount / (oldbalanceOrg + 1)`

Purpose:
- Detects relative transaction size.
- Highlights unusually large payments.

## F2: Log Amount
`log(amount + 1)`

Purpose:
- Improves model sensitivity to small vs large payments.
- Reduces skew.

---

# 2. Balance-Derived Features

## F3: Sender Balance Change
`oldbalanceOrg - newbalanceOrig`

This should equal `amount`. Deviations indicate anomalies.

## F4: Receiver Balance Change
`newbalanceDest - oldbalanceDest`

Should equal `amount`.

## F5: Sender Balance Ratio
`newbalanceOrig / (oldbalanceOrg + 1)`

Detects sudden drops.

---

# 3. Time-Based Features

## F6: Hour of Day
`step % 24`

Helps detect:
- Late-night fraud
- Unusual cash-out times

## F7: Transaction Velocity
Count of transactions within past `N` steps for sender.

Common thresholds:
- N = 1 hour (step window = 1)
- N = 24 hours (step window = 24)

---

# 4. Transaction-Type Features

## F8: One-Hot Encoding of Type
`CASH-IN`, `CASH-OUT`, `TRANSFER`, `PAYMENT`, `DEBIT`

## F9: High-Risk Type Flag
`1` if `type` in (`TRANSFER`, `CASH_OUT`) else `0`.

---

# 5. Behavioral Features

## F10: Is New Destination
`1` if destination account first appears in dataset.

## F11: Is New Sender
`1` if sender has < 3 previous transactions.

## F12: Amount Spike Relative to Sender History
`amount > (sender_avg_amount × 10)`

---

# 6. Ledger Validation Features

## F13: Sender Ledger Error
`abs(oldbalanceOrg - amount - newbalanceOrig)`

## F14: Receiver Ledger Error
`abs(newbalanceDest - oldbalanceDest - amount)`

High values indicate manipulated balances or fraud chain behavior.

---

# 7. Purpose of This Document

ML models, LLM explanations, and SQL queries use these engineered features to:
- Improve prediction accuracy,
- Enhance interpretability,
- Strengthen fraud chain detection.
