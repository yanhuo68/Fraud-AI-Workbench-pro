# Database Schema Reference

_Last Updated: 2026-02-22T22:31:59Z_

This document provides exact schema definitions for all tables stored in the database. LLMs must refer to these field names to avoid SQL hallucinations.

---

## Table of Contents

- [fraud_detection_dataset_mock_data_csv](#fraud_detection_dataset_mock_data_csv)

---

## fraud_detection_dataset_mock_data_csv

### Primary Key
- None detected

### Foreign Keys
- None detected

### Columns

| Column Name | Type | Nulls | Sample Value |
|-------------|------|-------|-------------|
| `Transaction_ID` | TEXT | 0 | T1 |
| `User_ID` | INTEGER | 0 | 4174 |
| `Transaction_Amount` | REAL | 2520 | 1292.76 |
| `Transaction_Type` | TEXT | 0 | ATM Withdrawal |
| `Time_of_Transaction` | REAL | 2552 | 16.0 |
| `Device_Used` | TEXT | 2474 | Tablet |
| `Location` | TEXT | 2547 | San Francisco |
| `Previous_Fraudulent_Transactions` | INTEGER | 0 | 0 |
| `Account_Age` | INTEGER | 0 | 119 |
| `Number_of_Transactions_Last_24H` | INTEGER | 0 | 13 |
| `Payment_Method` | TEXT | 2468 | Debit Card |
| `Fraudulent` | INTEGER | 0 | 0 |

### Metadata
- **Total Rows**: 51,005
- **Total Columns**: 12
- **Memory Usage**: 18.41 MB

---

## Key Schema Characteristics

### General Notes
- All schemas are auto-generated from uploaded CSV files
- Primary keys are detected using heuristics (unique, non-null columns)
- Foreign keys are detected by matching column names and value overlaps
- NULL counts indicate data quality issues

### Purpose of This Document
LLMs rely on this schema reference to:
- Avoid invalid SQL queries
- Construct correct joins and filters
- Reference applicable columns for analysis
- Understand relationships between tables
