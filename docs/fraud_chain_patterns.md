
---

# 📒 **4. docs/fraud_chain_patterns.md**

```markdown
# Fraud Chain Patterns in Online Payments

Fraud chains represent multi-step workflows used by fraudsters to move stolen funds through multiple accounts. This document defines reliable fraud chain patterns that LLMs should use when analyzing transactions.

---

# 1. Transfer → Cash-Out Chain (Most Common)

Sequence:
1. Fraudster initiates a large `TRANSFER`.
2. Funds arrive in a mule account (`nameDest`).
3. Mule immediately performs `CASH_OUT`.
4. Sender and destination balances show inconsistencies.

SQL pattern for detection:
```sql
SELECT t1.*, t2.*
FROM transactions t1
JOIN transactions t2
  ON t1.nameDest = t2.nameOrig
WHERE t1.type = 'TRANSFER'
  AND t2.type = 'CASH_OUT'
  AND t1.step + 1 = t2.step;

# 2. Multi-Hop Laundering Chain
Example chain:
Account A → Account B
Account B → Account C
Account C → Cash-out or exit point

Signals:
Transfers in consecutive step values.
Increasing complexity of routing.
No normal activity between transfers.

# 3. Smurfing + Consolidation
Pattern:
Multiple small incoming transfers to one account.
Large outgoing transfer from that account.

Risk indicators:
High count of transactions into one destination.
Large single cash-out afterwards.

# 4. Zero-Balance High-Value Chains

Fraudster uses empty accounts for transfers:
oldbalanceOrg = 0
amount is unusually high
No historical transactions for the sender

These appear frequently in simulation datasets.

# 5. Dormant Account Activation

Pattern:
Account with no prior activity suddenly receives large transfer.
Immediate cash out or second transfer.

# 6. Purpose of This Document

This guide helps LLMs
Detect complex fraud patterns
Relate SQL results to known fraud schemes
Provide deeper explanations in the UI


---

# 🎉 Your Fraud Knowledge-Base is now world-class  

With all **7 documents**, your RAG system now contains:

### ✔ Core fraud definitions  
### ✔ Risk rules  
### ✔ Model interpretation knowledge  
### ✔ SQL pattern playbook  
### ✔ User intent interpretation  
### ✔ Multi-step fraud chain detection  

This gives your LLM agents extremely clear structure and deep domain knowledge.

---

# Want even more?  
I can also generate:

📄 **docs/feature_engineering_guide.md**  
📄 **docs/database_schema_reference.md**  
📄 **docs/data_dictionary.md**  
📄 **docs/fraud_alert_policy.md**  
📄 **docs/business_explanation_templates.md**  

Just tell me:  
👉 **“Yes, generate more domain docs.”**
