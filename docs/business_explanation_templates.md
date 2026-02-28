# Business Explanation Templates for Fraud Analysis

This document provides template structures for LLMs to generate business-friendly explanations. Useful in the Streamlit “Explanation” tab and for auto-generated reports.

---

# 1. Explanation Template for High-Risk Transactions

**Summary:**  
The transaction appears high-risk due to the following indicators:

1. [Indicator 1: e.g., Large transaction amount]
2. [Indicator 2: e.g., Balance inconsistency]
3. [Indicator 3: e.g., New destination account]
4. [Indicator 4: e.g., Transaction type associated with fraud]

**Impact:**  
A fraudulent transaction could result in loss of funds or unauthorized account use.

**Recommendation:**  
Flag for immediate manual review and verify sender identity.

---

# 2. Explanation Template for Fraud Chain Detection

**Summary:**  
This transaction is part of a suspicious transfer chain.

**Chain Elements Identified:**
1. Initial transfer from [Account A].
2. Immediate cash-out by [Account B].
3. Ledger inconsistencies in sender or receiver balances.

**Risk Level:** High.

**Recommendation:**  
Investigate all accounts involved and review related transactions.

---

# 3. Explanation Template for Anomaly Detection (Isolation Forest)

**Summary:**  
The model assigned a high anomaly score due to:

1. Unusual amount compared to sender history.
2. Rare or risky transaction type.
3. Irregular balance transition.
4. Activity spike inconsistent with typical behavior.

**Next Steps:**  
Review the sender’s recent activity and confirm account ownership.

---

# 4. Explanation Template for False Positives

**Summary:**  
This transaction was flagged incorrectly because:

1. Legitimate customer behavior,
2. No fraud chain elements detected,
3. Balance transitions are valid,
4. Transaction amount aligns with customer history.

**Recommendation:**  
Mark as safe but monitor account for further unusual activity.

---

# Purpose of This Document
These templates ensure:
- Clear explanations for end-users,
- Standardized reasoning,
- Higher consistency in LLM output,
- Better UI communication in fraud dashboards.
