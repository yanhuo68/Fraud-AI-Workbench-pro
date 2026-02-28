# SQL Patterns for Fraud Detection
This document provides reliable SQL query patterns used for fraud analysis in the Online Payments Fraud dataset. LLMs should use these patterns when generating SQL queries.

---

# 1. Basic SQL Patterns

## 1.1 Count Total Transactions
```sql
SELECT COUNT(*) FROM transactions;
## 1.2 Count Fraud vs Non-Fraud
SELECT isFraud, COUNT(*) 
FROM transactions 
GROUP BY isFraud;
## 1.3 Percentage of Fraudulent Transactions
SELECT 
  (SUM(CASE WHEN isFraud = 1 THEN 1 ELSE 0 END) * 100.0) /
  COUNT(*) AS fraud_percentage
FROM transactions;

# 2. Amount-Based Fraud Queries

## 2.1 Top 10 Largest Fraud Transactions
SELECT *
FROM transactions
WHERE isFraud = 1
ORDER BY amount DESC
LIMIT 10;

## 2.2 High Amount Suspicious Transactions (Rule TR-1)
SELECT *
FROM transactions
WHERE amount > (
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amount)
)
ORDER BY amount DESC;

# 3. Balance Consistency Queries
## 3.1 Validate Sender Balance Ledger
SELECT *
FROM transactions
WHERE oldbalanceOrg - amount != newbalanceOrig;

## 3.2 Validate Receiver Balance Ledger
SELECT *
FROM transactions
WHERE oldbalanceDest + amount != newbalanceDest;

# 4. Fraud Chain (Transfer → Cash-Out)
## 4.1 Transfers Followed by Immediate Cash-Out
SELECT t1.*, t2.*
FROM transactions t1
JOIN transactions t2
  ON t1.nameDest = t2.nameOrig
WHERE t1.type = 'TRANSFER'
  AND t2.type = 'CASH_OUT'
  AND t1.step + 1 = t2.step;

# 5. Mule Account Detection
## 5.1 Destinations That Only Receive Funds
SELECT nameDest, COUNT(*) AS receive_count
FROM transactions
GROUP BY nameDest
HAVING SUM(CASE WHEN type = 'CASH_OUT' THEN 1 ELSE 0 END) = 0
ORDER BY receive_count DESC;

# 6. Zero-Balance Manipulation
## 6.1 Suspicious Zero-Balance Transactions
SELECT *
FROM transactions
WHERE oldbalanceOrg = 0 AND amount > 0;