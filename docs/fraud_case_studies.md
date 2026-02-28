# Fraud Case Studies for LLM Reasoning

This document provides realistic case studies that LLMs can reference when evaluating new transactions or interpreting SQL results.

---

# Case Study 1: Classic Transfer → Cash-Out Fraud

## Summary
A fraudster steals account access and sends a large transfer. The receiving account immediately cashes out the funds.

## Indicators
- `TRANSFER` followed by `CASH_OUT`
- Steps differ by 1 hour
- Balance inconsistencies appear
- Destination is a new account

## Example SQL
See: fraud_sql_patterns → Section 4.1

---

# Case Study 2: Multi-Hop Laundering Chain

## Summary
Funds move through 3–6 accounts in quick succession.

## Indicators
- Sequential steps
- Increasingly small balance changes
- Final cash-out

## Risk Level
Very high.

---

# Case Study 3: Dormant Account Activation

## Summary
A dormant account suddenly receives a high-value transfer.

## Indicators
- No prior activity for 100+ hours
- High amount
- Immediate outgoing transfer

---

# Case Study 4: Smurfing → Consolidation Fraud

## Summary
Multiple small transactions funnel into one account, followed by one large outgoing transaction.

## Indicators
- Many incoming transactions
- One large outgoing payment
- Balances inconsistent with normal behavior

---

# Purpose of This Document
These case studies help LLM agents:
- Recognize complex patterns
- Explain suspicious activity clearly
- Reference realistic scenarios
