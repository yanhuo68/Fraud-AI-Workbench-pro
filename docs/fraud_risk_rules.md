# Fraud Risk Rules for Online Payments

This document defines clear, authoritative rules used to evaluate fraud risk in online payment transactions. These rules represent both domain knowledge and patterns observed in the dataset.

The rules use exact terms such as `sender account`, `destination account`, `balance inconsistency`, and `amount spike` so LLMs can reference them reliably.

---

# 1. Behavioral Risk Indicators

## Rule BR-1: Amount Spike Relative to History
A transaction is high-risk if its `amount` is significantly larger than what the sender has previously transferred.

Indicators:
- Amount > 10 × historical average for the sender.
- Amount > 95th percentile of sender transaction distribution.

## Rule BR-2: Velocity Anomalies
Risk increases when:
- More than 5 transactions from the same sender occur within 1 hour (`step` proximity).
- Many small transactions followed by one large transfer (“smurfing” pattern).

## Rule BR-3: Suspicious Timing
- Activity bursts at unusual times (e.g., late-night hours).
- Large transfers immediately after account login.

---

# 2. Balance-Based Risk Rules

## Rule B-1: Impossible Balance Transitions
Sender balances must satisfy:
oldbalanceOrg - amount = newbalanceOrig
If not, the transaction is suspicious.

## Rule B-2: Destination Balance Should Increase Properly
Receiver balances must satisfy:
oldbalanceDest + amount = newbalanceDest


If the destination balance does not change, risk increases.

## Rule B-3: Zero-Balance High-Amount Transfers
If `oldbalanceOrg = 0` and `amount > 0`, the transaction is highly suspicious.

## Rule B-4: Negative or Unstable Balances
A transaction is suspicious when:
- Balances become negative.
- Balances fluctuate in ways that violate expected ledger behavior.

---

# 3. Account Activity Risk Rules

## Rule A-1: New Accounts Performing Large Transfers
Accounts with short history that immediately send high amounts are high-risk.

## Rule A-2: Dormant Accounts Reactivated
Long-idle accounts showing sudden large activity are suspicious.

## Rule A-3: Destination Accounts Without Cash-Out Activity
Accounts that receive large transfers but never perform `CASH_OUT` may indicate money mule behavior.

---

# 4. Fraud Chain Patterns

## Pattern F-1: Transfer → Immediate Cash-Out
Fraud chain:
1. Large `TRANSFER` to mule account.
2. Mule performs immediate `CASH_OUT`.
3. Sender account returns to zero balance or remains inconsistent.
4. Mule account shows no normal activity before or after chain.

This pattern has a strong correlation with `isFraud = 1`.

## Pattern F-2: Multi-Hop Routing
Funds transferred sequentially through multiple accounts within short time windows.

## Pattern F-3: Repeated Transfers into Same Destination
High-risk when multiple senders funnel funds into the same destination account.

---

# 5. Threshold Rules for Suspicion

- **TR-1:** `amount` is in the top 1% of all transactions.  
- **TR-2:** More than 3 balance inconsistencies detected for the sender.  
- **TR-3:** Transfer to a destination account that has never appeared before.  
- **TR-4:** Sender performs > 10 transactions within the same `step` window.

---

# 6. How to Use These Rules

These rules help:
- Isolation Forest explain anomalies.
- Random Forest interpret predictions.
- LLMs give precise explanations.
- SQL queries identify suspicious subsets.
- Knowledge-based RAG refine risk scoring.

Rules are not deterministic but serve as strong indicators of potential fraud.
