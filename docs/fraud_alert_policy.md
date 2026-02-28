# Fraud Alert Policy Guidelines

This document defines how fraud alerts should be triggered, ranked, and reviewed. These guidelines help LLMs produce consistent and reliable recommendations.

---

# 1. Alert Severity Levels

## Level 1 — High Severity
Triggers:
- Fraud probability > 0.9
- Isolation Forest anomaly score > 0.9
- Repeated balance inconsistencies
- Zero-balance high-amount cases

Action:
- Immediate manual review.

---

## Level 2 — Medium Severity
Triggers:
- Fraud probability between 0.6 and 0.9
- Unknown destination accounts receiving large amounts
- Suspicious multi-hop transfers

Action:
- Queue for fraud analyst review.

---

## Level 3 — Low Severity
Triggers:
- Small unusual transactions
- mild deviations from typical patterns

Action:
- Monitor but no immediate action.

---

# 2. Alert Justification Requirements

Alerts must include:
- Specific rule violated (e.g., B-1 ledger failure).
- Relevant transaction features.
- Suggested next steps.

Example justification:
“Transaction violates Rule B-1: Sender ledger inconsistency. Amount is large relative to zero balance. Recommend full review.”

---

# 3. Escalation Policy

- High-severity alerts → reviewed within 1 hour.
- Medium-severity → reviewed within 24 hours.
- Low-severity → monitored only.

---

# 4. Purpose of This Document

LLMs use this to:
- Provide consistent recommendations,
- Prioritize alerts,
- Generate explainable output during fraud analysis.
