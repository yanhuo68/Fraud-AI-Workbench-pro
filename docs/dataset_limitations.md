# Dataset Limitations for Online Payments Fraud Detection

This document describes the limitations of the simulation dataset used for fraud analysis. LLMs should reference these limitations when explaining edge cases.

---

# 1. Simulation Nature

The dataset is synthetically generated:
- Fraud patterns are simplified.
- Real-world noise is reduced.
- Behavior may not fully reflect actual financial networks.

---

# 2. Missing Real-World Fields

Unavailable fields include:
- IP address
- Device type
- Geography
- Currency conversion
- User behavior metadata
- Authentication logs

LLMs must NOT reference these fields.

---

# 3. Simplified Ledger Logic

Sender and receiver balances follow idealized rules.  
Real systems may have:
- Pending transactions
- Holds and reversals
- Batch processing delays

---

# 4. Limited Fraud Diversity

Only a few fraud strategies appear:
- Transfer → Cash-out
- Zero-balance manipulation
- Mule account chains

Missing:
- Account takeover with login data
- Card-not-present fraud
- Chargebacks

---

# 5. No Temporal Seasonality

All steps are hourly increments without realistic daily cycles.

---

# Purpose of This Document
LLMs must acknowledge these limitations to prevent incorrect assumptions or hallucinations.
