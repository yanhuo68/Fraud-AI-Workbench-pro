# Data Dictionary for Online Payments Fraud Dataset

This data dictionary provides precise definitions for every field in the `transactions` dataset. LLMs use this dictionary for accurate SQL generation and model explanations.

---

# Field Definitions

## `step`
- Integer.
- One unit = one hour.
- Represents time progression in the dataset.

## `type`
- Categorical string.
- Valid values:
  - `CASH-IN`
  - `CASH-OUT`
  - `TRANSFER`
  - `PAYMENT`
  - `DEBIT`

## `amount`
- Transaction amount in floating point.
- Higher values correlate with higher fraud risk.

## `nameOrig`
- Sender account ID.
- String identifier.

## `oldbalanceOrg`
- Sender account balance before the transaction.

## `newbalanceOrig`
- Sender balance after the transaction.
- Ideally satisfies:
newbalanceOrig = oldbalanceOrg - amount


## `nameDest`
- Receiver account ID.

## `oldbalanceDest`
- Receiver balance before the transaction.

## `newbalanceDest`
- Receiver balance after the transaction.
- Should satisfy:
newbalanceDest = oldbalanceDest + amount


## `isFraud`
- `1` if transaction is fraudulent, else `0`.
- Fraud mostly occurs in `TRANSFER` and `CASH_OUT`.

## `isFlaggedFraud`
- Indicates system-flagged suspicious transactions.
- Does not always equal `isFraud`.

---

# Purpose of This Document
- Provide explicit, correct column definitions.
- Help LLM reason about balance logic.
- Improve SQL validity and fraud explanations.

