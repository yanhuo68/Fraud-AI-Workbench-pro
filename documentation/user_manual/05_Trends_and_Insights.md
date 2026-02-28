# 📈 Trends & Insights — User Manual

**Page:** Trends & Insights (`pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)`)  
**Access Level:** Authenticated Users

---

## Overview

The **Trends & Insights** page provides automated statistical analysis and visualization of fraud datasets. It supports both single-table exploratory data analysis (EDA) and multi-table smart joins for cross-dataset correlation. AI-generated narrative summaries and exportable PDF reports are included.

---

## Interface Layout

```
┌────────────────────────────────────────────────┐
│ Sidebar: Table selector, analysis options       │
├────────────────────┬───────────────────────────┤
│ EDA Charts         │ AI Narrative Summary       │
├────────────────────┴───────────────────────────┤
│ Smart Join Panel (multi-table)                  │
├─────────────────────────────────────────────────┤
│ Export PDF button                               │
└─────────────────────────────────────────────────┘
```

---

## Tabs / Sections

### Section 1 — 📊 Single-Table EDA

**How to use:**
1. Select a table from the **Table** dropdown in the sidebar.
2. Select columns to analyze (or select all).
3. Click **▶ Run EDA Analysis**.

**Automatic visualizations generated:**

| Chart Type | When Shown |
|---|---|
| Histogram | Numeric columns — value distribution |
| Bar Chart | Categorical columns — frequency counts |
| Time-Series Line Chart | Datetime columns — trend over time |
| Box Plot | Outlier detection per numeric column |
| Correlation Heatmap | Pairwise correlation between numeric columns |
| Missing Value Summary | Null rate per column |

**AI Narrative:**  
Below the charts, an AI-generated paragraph summarizes key findings, anomalies, and fraud-relevant patterns observed in the data.

---

### Section 2 — 🔗 Smart Multi-Table Join

Automatically detects primary/foreign key relationships between tables and performs joins for cross-dataset analysis.

**How to use:**
1. Select 2 or more tables from the **Multi-Table Selector**.
2. Click **▶ Run Smart Join**.
3. The system infers join conditions based on column name matches and data types.
4. Results are shown as a merged table with additional correlation charts.

**Smart join intelligence:**
- Detects `id` / `*_id` column pairs across tables
- Falls back to name-similarity matching if no exact key match
- Shows detected join path as a readable expression (e.g., `transactions.customer_id → customers.id`)

---

### Section 3 — 📉 Time-Series Anomaly Detection

If a datetime column is present, the system automatically detects anomalous time periods.

**Algorithm:**
- Rolling average with configurable window size
- Z-score thresholding (default: ±2.5 sigma)
- Anomalous spikes highlighted in red on the time-series chart

**Configurable options (sidebar):**
- **Time column** — which datetime column to use
- **Value column** — the metric to track over time
- **Window size** — rolling average window (in rows)
- **Threshold** — Z-score cutoff for anomaly flagging

---

### Section 4 — 📑 Export PDF Report

Click **📑 Export Board-Ready PDF** to generate a formatted report containing:
- Dataset summary (row/column counts, data types)
- All generated charts embedded as images
- AI narrative summary
- Detected anomalies table
- Timestamp and analyst metadata

The PDF downloads automatically to your browser.

---

## Sidebar Options

| Option | Description |
|---|---|
| **Table** | Primary table for single-table EDA |
| **Columns** | Which columns to include in analysis |
| **Multi-Table** | Tables for smart join analysis |
| **LLM** | Model used for AI narrative generation |
| **Time Column** | Datetime column for anomaly detection |
| **Value Column** | Metric column for time-series |
| **Window** | Rolling average window size |
| **Z-Threshold** | Anomaly detection sensitivity |

---

## Tips

- Run single-table EDA first to understand your data before attempting multi-table joins.
- The correlation heatmap is most useful when you have 3+ numeric columns.
- For time-series anomaly detection, ensure your datetime column is in ISO format (`YYYY-MM-DD HH:MM:SS`).
- PDF reports are useful for sharing investigation findings with non-technical stakeholders.
