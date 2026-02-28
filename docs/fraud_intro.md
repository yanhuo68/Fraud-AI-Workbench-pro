# Introduction to Online Payments Fraud

Online payments fraud refers to any unauthorized or deceptive financial transaction designed to illegally obtain money or value. Fraud often emerges when attackers exploit weak identity verification, poor monitoring, or gaps in digital financial systems.

Fraudsters commonly use:
- Stolen or synthetic identities.
- Account takeover techniques.
- Automated scripts to trigger many transactions quickly.
- Money mule accounts to receive and cash out illicit transfers.

Fraud detection aims to identify unusual patterns that differ from legitimate customer behavior.

---

## 1. Overview of the Online Payments Fraud Dataset

This dataset simulates realistic online payment transactions. Each row represents one financial transaction with metadata about balances, transaction type, and fraud labels.

### **Key fields**

| Field | Description |
|-------|-------------|
| `step` | Time step in hours. One step equals one hour. |
| `type` | Transaction type (`CASH-IN`, `CASH-OUT`, `TRANSFER`, `PAYMENT`, `DEBIT`). |
| `amount` | Amount transferred in the transaction. |
| `oldbalanceOrg` | Sender’s balance before the transaction. |
| `newbalanceOrig` | Sender’s balance after the transaction. |
| `oldbalanceDest` | Receiver’s balance before receiving funds. |
| `newbalanceDest` | Receiver’s balance after receiving funds. |
| `isFraud` | 1 if the transaction is fraudulent; otherwise 0. |
| `isFlaggedFraud` | 1 if the system flagged the transaction as suspicious. |

---

## 2. Core Concepts in Fraud Detection

### **Authorized vs Unauthorized Activity**
- Authorized: A legitimate customer initiates a transaction.
- Unauthorized: A fraudster initiates the transaction without permission.

### **Behavioral Signals**
Fraud transactions often show deviations such as:
- Unusual amounts relative to the customer history.
- Sudden balance increases or decreases.
- Abnormal transaction types.
- Irregular timing (late night or rapid bursts).

### **Account Takeover (ATO)**
In ATO cases:
- Account behavior changes abruptly.
- Large `TRANSFER` or `CASH_OUT` transactions occur.
- Balance patterns fail to match typical customer habits.

---

## 3. Common Fraud Patterns in This Dataset

Patterns frequently associated with `isFraud = 1` include:

### **Pattern A: Transfer → Cash-out Fraud Chain**
1. Fraudster initiates a large `TRANSFER`.  
2. Funds arrive in a mule account.  
3. Mule performs immediate `CASH_OUT`.  
4. Sender and mule accounts show abnormal balance transitions.

### **Pattern B: Zero-Balance Manipulation**
Examples:
- `oldbalanceOrg = 0` AND `amount > 0`.  
- Sender balance does not align with final `newbalanceOrig`.

This suggests fabricated ledger behavior or unauthorized activity.

### **Pattern C: Destination Account with No History**
When `oldbalanceDest = 0` but receives unusually high amounts, risk increases.

### **Pattern D: Inconsistent Balances**
If:
oldbalanceOrg - amount != newbalanceOrig
or
oldbalanceDest + amount != newbalanceDest
this indicates anomalies.

---

## 4. Fraud Detection Methods Used in This Project

### **Anomaly Detection**
- Isolation Forest identifies unusual transactions.
- Unusual amounts, irregular balances, or rare type combinations appear as outliers.

### **Supervised Classification**
- Random Forest estimates the probability that a transaction is fraudulent.
- The model learns patterns between features and `isFraud`.

### **LLM-Assisted Analysis**
- LLMs interpret SQL results.
- LLMs explain anomalies in natural language.
- RAG provides contextual fraud knowledge to improve reliability.

---

## 5. Purpose of This Document

This introduction gives foundational fraud concepts for all LLM-based analysis in the system.  
LLMs use these facts to:
- Interpret SQL query results.
- Provide explanations.
- Detect balance inconsistencies.
- Identify key fraud patterns.
