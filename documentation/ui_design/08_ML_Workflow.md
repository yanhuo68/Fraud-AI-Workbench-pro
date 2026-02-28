# 🔄 ML Workflow — UI Design Specification

**Page:** `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────────────────────────────────────────┐
│  🔄 ML Workflow                              [st.title]      │
│  "Train, evaluate, and deploy..."            [st.caption]    │
├──────────────────────────────────────────────────────────────┤
│  [ 📂 Dataset ] [ 🔧 Train ] [ 📊 Evaluate ] [ 🚀 Deploy ]  │  ← 4 tabs
├──────────────────────────────────────────────────────────────┤
│  [Tab content area]                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Tab 1 — 📂 Dataset Preparation

```
┌─────────────────────────┬────────────────────────────────────┐
│  [Table ▾]              │  📋 Dataset Preview                │
│  [Label column ▾]       │  ─────────────────────────────     │
│  [Feature columns ▾]    │  [st.dataframe sample — 10 rows]  │
│  (multi-select)         │                                    │
│  ── Split Ratios ──     │  📊 Column Type Summary           │
│  Train: [──●──] 70%     │  Numeric: 8 columns               │
│  Val:   [─●───] 15%     │  Categorical: 3 columns           │
│  Test:  [─●───] 15%     │  DateTime: 1 column               │
│                         │  Null rate: 2.1%                  │
│  [Dataset version name] │                                    │
│  [💾 Save Dataset]      │  [st.metric("Rows", 10,240)]      │
└─────────────────────────┴────────────────────────────────────┘
```

---

## Tab 2 — 🔧 Train Model

```
┌──────────────────────┬─────────────────────────────────────────┐
│  Algorithm           │  Hyperparameters                        │
│  ○ XGBoost  ● RF     │  n_estimators: [──●──] 200             │
│                      │  max_depth:    [─●───] 6               │
│  Dataset Version ▾   │  learning_rate: 0.1    (XGB only)      │
│                      │  subsample:    0.8     (XGB only)      │
│                      │  min_samples:  2       (RF only)       │
│                      │                                         │
│                      │  [▶ Train Model]  [primary, full-width] │
│                      │                                         │
│                      │  ── Training Progress ──               │
│                      │  [st.progress bar]                     │
│                      │  Epoch 3/10 · loss: 0.243              │
│                      │  [Live loss line chart]                 │
└──────────────────────┴─────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Algorithm selector | `st.radio("Algorithm", ["XGBoost", "RandomForest"], horizontal=True)` |
| Hyperparameter sliders | `st.slider()` per param — range varies by algorithm |
| Train button | `st.button("▶ Train Model", type="primary", use_container_width=True)` |
| Progress bar | `st.progress(epoch/total_epochs)` |
| Caption | `st.caption(f"Epoch {e}/{n} · loss: {loss:.3f}")` |
| Loss chart | `st.line_chart(loss_history)` — live-updating via `st.rerun()` |

---

## Tab 3 — 📊 Evaluate

```
┌──────────────────────────────────────────────────────────────┐
│  📊 Performance Metrics                                       │
│  ─────────────────────────────────                           │
│  [Accuracy] [Precision] [Recall] [F1] [ROC-AUC]             │  ← 5-col metrics
│    0.947       0.923      0.871    0.896   0.981             │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │   Confusion Matrix   │  │   ROC Curve                  │ │
│  │   [Heatmap 2×2]      │  │   [Line chart AUC=0.981]     │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  🔍 SHAP Explainability                                       │
│  [🔍 Generate SHAP Explanation]   [secondary button]         │
│  [Feature importance bar chart]                              │
│  [Beeswarm plot]                                             │
│  [Waterfall for individual prediction]                       │
├──────────────────────────────────────────────────────────────┤
│  📋 Cross-Model Comparison                                    │
│  [st.dataframe — model version comparison table]            │
└──────────────────────────────────────────────────────────────┘
```

| Metric card | Colour |
|---|---|
| Accuracy ≥ 0.90 | `#2ecc71` green delta |
| Recall < 0.70 | `#e74c3c` red delta |
| All others | Neutral |

### Confusion Matrix Heatmap
- 2×2 grid: TP (green), TN (green), FP (orange), FN (red)
- Annotated with counts and percentages
- Generated via `plotly.graph_objects.Heatmap`

### SHAP Charts
All SHAP charts use Plotly with dark theme:
- Feature importance: horizontal bar, sorted descending, `#61affe` fill
- Beeswarm: dot-plot per feature, coloured by feature value (`viridis` palette)
- Waterfall: individual prediction breakdown, green/red bars

---

## Tab 4 — 🚀 Deploy

```
┌──────────────────────────────────────────────────────────────┐
│  Model version: [xgboost_v3 ▾]                               │
│                                                              │
│  [🚀 Deploy as Scoring API]   [primary button]              │
│                                                              │
│  ── Test Deployment ──                                       │
│  [Feature inputs form — one row per feature]                 │
│  feature_1: [──────────] (number input)                     │
│  feature_2: [──────────]                                    │
│                                                              │
│  [▶ Test Score]   →   Score: 0.87 (HIGH RISK 🔴)            │
└──────────────────────────────────────────────────────────────┘
```

| Risk Score | Badge Colour |
|---|---|
| ≥ 0.75 | `#e74c3c` red — HIGH RISK 🔴 |
| 0.50–0.74 | `#f39c12` orange — MEDIUM RISK 🟡 |
| < 0.50 | `#2ecc71` green — LOW RISK 🟢 |

---

## Colour Summary

| Element | Colour |
|---|---|
| Loss chart line | `#ff4b4b` red |
| Accuracy badge (high) | `#2ecc71` |
| Accuracy badge (low) | `#e74c3c` |
| SHAP bars | `#61affe` blue |
| TP / TN cells | `#2ecc71` green |
| FP / FN cells | `#e74c3c` red |
