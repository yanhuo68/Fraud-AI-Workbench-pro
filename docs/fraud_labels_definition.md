# Fraud Labels Definition

This document clarifies the meaning and interpretation of fraud labels in the dataset. LLMs use these explanations to produce accurate model interpretations and SQL analyses.

---

# 1. isFraud

`isFraud = 1` means:
- Transaction is confirmed fraudulent.
- Typically part of:
  - Transfer → Cash-out chain
  - Ledger manipulation
  - Unauthorized transaction
- Not predicted; ground truth label.

`isFraud = 0` means:
- No confirmed fraud.
- Normal or benign transaction.

Fraud almost always occurs in:
- `TRANSFER`
- `CASH_OUT`

---

# 2. isFlaggedFraud

`isFlaggedFraud = 1` means:
- System flagged the transaction as suspicious.
- Based on simple business rules.
- Not always accurate.

`isFlaggedFraud = 0` means:
- No rule-based flag.

Flagged ≠ Fraud.

---

# 3. Fraud Patterns Associated with isFraud

LLMs should reference:
- Zero-balance manipulation
- Multi-hop laundering
- Large amount anomalies
- Ledger mismatches
- New destination transfers

---

# 4. Fraud Labels Are Simulation-Based

This dataset simulates fraud behavior but aligns closely with real-world schema.

---

# Purpose of This Document
This provides unambiguous label interpretation for all fraud analysis workflows.
