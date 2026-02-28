# 📈 Trends & Insights — UI Design Specification

**Page:** `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌────────────────────┬─────────────────────────────────────────────┐
│   SIDEBAR EXTRAS   │  📈 Trends & Insights          [st.title]  │
│                    │  "Automated EDA & anomaly..."  [st.caption] │
│  [Table ▾]         ├─────────────────────────────────────────────┤
│  [Columns ▾]       │  ┌──────────────────────────────────────┐  │
│  (multi-select)    │  │  Single-Table EDA Section             │  │
│  [LLM ▾]           │  │  [Chart gallery — 2-3 cols]          │  │
│  [Multi-Table ▾]   │  │  [AI Narrative text block]           │  │
│  ── Time Series ── │  └──────────────────────────────────────┘  │
│  [Time column ▾]   │  ┌──────────────────────────────────────┐  │
│  [Value column ▾]  │  │  Smart Join Section                   │  │
│  [Window ─●─]      │  │  [Merged table + correlation charts] │  │
│  [Threshold ─●─]   │  └──────────────────────────────────────┘  │
│                    │  ┌──────────────────────────────────────┐  │
│  [▶ Run EDA]       │  │  Time-Series Anomaly Section         │  │
│  [▶ Smart Join]    │  │  [Line chart + anomaly markers]      │  │
│  [📑 Export PDF]   │  └──────────────────────────────────────┘  │
└────────────────────┴─────────────────────────────────────────────┘
```

---

## Sidebar Controls

| Element | Spec |
|---|---|
| Table dropdown | `st.selectbox("Primary Table", tables)` |
| Column selector | `st.multiselect("Columns to Analyse", columns)` |
| LLM dropdown | `st.selectbox("Narrative LLM", llms)` |
| Multi-table selector | `st.multiselect("Multi-Table Join", all_tables)` |
| Time column | `st.selectbox("Time Column", datetime_columns)` |
| Value column | `st.selectbox("Value Column", numeric_columns)` |
| Window slider | `st.slider("Window Size", 3, 30, 7)` |
| Z-threshold slider | `st.slider("Anomaly Threshold (σ)", 1.0, 4.0, 2.5, 0.1)` |
| Run EDA button | `st.button("▶ Run EDA Analysis", type="primary")` |
| Smart Join button | `st.button("▶ Run Smart Join", type="primary")` |
| Export button | `st.button("📑 Export PDF Report")` |

---

## Single-Table EDA Charts Grid

Chart rows arranged in 2-column layout:

```
┌─────────────────────────┬───────────────────────────┐
│  Histogram (numeric)    │  Bar Chart (categorical)  │
├─────────────────────────┼───────────────────────────┤
│  Box Plot (outliers)    │  Correlation Heatmap      │
├─────────────────────────┴───────────────────────────┤
│  Time-Series Line Chart (if datetime col present)   │
├─────────────────────────────────────────────────────┤
│  Missing Value Summary bar chart (always shown)     │
└─────────────────────────────────────────────────────┘
```

| Chart | Library | Config |
|---|---|---|
| Histogram | Plotly / Altair | Bin count auto, `#61affe` fill |
| Bar Chart | Plotly | Sorted descending, `#49cc90` fill |
| Box Plot | Plotly | Per-column, outliers marked red |
| Heatmap | Plotly / Seaborn | Diverging `RdBu` palette |
| Time-Series | Plotly | Line + area fill, `#ff4b4b` line |
| Missing Values | Plotly | Horizontal bar, red gradient fill |

Each chart wrapped in `st.plotly_chart(..., use_container_width=True)`.

---

## AI Narrative Block

Displayed below the chart gallery:

```
┌──────────────────────────────────────────────────────────┐
│  🤖 AI Analysis Summary                                  │
│  ──────────────────────────────────────────────────────  │
│  The transaction dataset shows a bimodal amount           │
│  distribution with a spike at $50–$200 and a long tail   │
│  above $5,000. The merchant column is dominated by        │
│  "TechMart" (18%) and "QuickCash" (12%), both of which   │
│  are flagged in fraud databases...                       │
└──────────────────────────────────────────────────────────┘
```

Rendered as: `st.markdown(narrative)` inside a styled `<div>` with glass card CSS.

---

## Smart Join Section

```
┌──────────────────────────────────────────────────────────┐
│  🔗 Smart Multi-Table Join                               │
│  Join path detected: transactions.customer_id → customers.id │
│  ──────────────────────────────────────────────────────  │
│  [st.caption("Joined 2 tables · 3,072 rows")]            │
│  [st.dataframe(joined_df, use_container_width=True)]     │
│                                                          │
│  [Correlation charts for numeric cross-table columns]    │
└──────────────────────────────────────────────────────────┘
```

---

## Time-Series Anomaly Chart

```
┌──────────────────────────────────────────────────────────┐
│  📉 Anomaly Detection — transaction_date × amount        │
│  ──────────────────────────────────────────────────────  │
│  [Plotly line chart]                                     │
│   ↑ amount                                               │
│   │        ●  ← anomalous spike (red marker)            │
│   │   ~~~●~~~~~~~~~~~~~~~~~~~~                           │
│   │                                                      │
│   └──────────────────────────────→ date                  │
│                                                          │
│  Rolling avg: blue line | Anomaly threshold: dashed red  │
│  ──────────────────────────────────────────────────────  │
│  Detected 3 anomalous periods (listed below chart)       │
│  [st.dataframe(anomaly_table)]                          │
└──────────────────────────────────────────────────────────┘
```

| Visual element | Spec |
|---|---|
| Normal line | `#61affe` blue, 2px width |
| Rolling avg | `#2ecc71` green, dashed |
| Anomaly threshold | `#e74c3c` red, dashed |
| Anomaly markers | `#ff4b4b` filled circles, size 12 |

---

## PDF Export Flow

1. Click `📑 Export Board-Ready PDF`.
2. `st.spinner("Generating PDF...")` shown.
3. `st.download_button("📥 Download Report", pdf_bytes, "fraud_trends_report.pdf")` appears.

---

## Colour Summary

| Element | Colour |
|---|---|
| Chart fill (primary) | `#61affe` blue |
| Chart fill (secondary) | `#49cc90` green |
| Anomaly markers | `#ff4b4b` red |
| Heatmap positive | `#e74c3c` |
| Heatmap negative | `#3498db` |
| Narrative block | Glass card `rgba(255,255,255,0.05)` |
