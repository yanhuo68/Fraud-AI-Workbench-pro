# 📁 Data Hub — UI Design Specification

**Page:** `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────────────────────────────────────┐
│  📁 Data Hub                     [st.title]              │
│  "Central data management..."   [st.caption]             │
├──────────────────────────────────────────────────────────┤
│  [ 📤 Upload ] [ 🗄️ Explorer ] [ 🕸️ Graph ] [ 🔬 Eval ] [ 🌍 Connectors ] │  ← 5 tabs
├──────────────────────────────────────────────────────────┤
│  [Tab content area — changes per tab]                    │
└──────────────────────────────────────────────────────────┘
```

---

## Tab Bar

5 tabs rendered via `st.tabs([...])`:

| # | Label | Icon |
|---|---|---|
| 1 | Upload Files | 📤 |
| 2 | Database Explorer | 🗄️ |
| 3 | Graph Visualizer | 🕸️ |
| 4 | Graph Evaluation | 🔬 |
| 5 | External Connectors | 🌍 |

---

## Tab 1 — 📤 Upload Files

```
┌──────────────────────────────────────────────────────────┐
│  [File uploader widget — drag & drop zone]               │
│  Accepted: csv, pdf, png, jpg, jpeg, mp3, mp4, sql       │
│                                                          │
│  [⬆️ Upload & Ingest]  [full-width primary button]       │
│                                                          │
│  [Status messages / spinner appear here]                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ✅ Table 'transactions' created — 1,024 rows      │   │  ← success info box
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  [Supported file types reference table]                  │
└──────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| File uploader | `st.file_uploader(type=[...])` — Streamlit default drag-drop |
| Upload button | `st.button("⬆️ Upload & Ingest", type="primary", use_container_width=True)` |
| Progress | `st.spinner("Uploading and processing...")` |
| Result display | `st.success()` / `st.error()` / `st.info()` contextual |

---

## Tab 2 — 🗄️ Database Explorer

```
┌──────────────┬──────────────────────────────────────────┐
│ [Table ▾]    │  🗄️ transactions                         │
│ (dropdown)   │  2,048 rows · 12 columns                 │
│              ├──────────────────────────────────────────┤
│              │  [Sortable / scrollable data table]      │
│              │  (first 100 rows displayed)              │
│              ├──────────────────────────────────────────┤
│              │  [📥 Download as CSV]                    │
└──────────────┴──────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Table selector | `st.selectbox("Table", tables)` — left sidebar or top of content |
| Data preview | `st.dataframe(df.head(100), use_container_width=True)` |
| Metadata | `st.metric("Rows", N)` + `st.metric("Columns", M)` side by side |
| Download | `st.download_button("📥 Download as CSV", data, file_name)` |

---

## Tab 3 — 🕸️ Graph Visualizer

```
┌──────────────────────────────────────────────────────────┐
│  [▶ Load Graph]  [🔄 Rebuild Graph*]  [📤 Project SQL*] │  ← action buttons row
├──────────────────────────────────────────────────────────┤
│                                                          │
│        [Interactive physics graph canvas]                │
│        Nodes: coloured by label                         │
│        Edges: directional arrows                         │
│        Hover: tooltip with properties                    │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Depth: [─────●────] slider   Node count: N             │
└──────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Graph renderer | `streamlit-agraph` / `pyvis` embedded HTML |
| Node colours | Each label type gets a distinct colour (auto-assigned) |
| Action buttons | Row of 3 buttons (`Load`, `Rebuild*`, `Project*`) — `*` = admin only |
| Depth slider | `st.slider("Depth", 1, 5, 2)` |
| Admin-only style | Non-admin buttons grayed out or hidden |

---

## Tab 4 — 🔬 Graph DB Evaluation

```
┌──────────────────────────────────────────────────────────┐
│  [▶ Run Full Evaluation]   [primary button]              │
├───────────────────┬──────────────────────────────────────┤
│  🏥 Connectivity  │  ⚡ Performance                      │
│  Nodes:  N        │  Avg latency: Xms                   │
│  Edges:  M        │  Index usage: Y%                     │
│  Orphans: K       │                                      │
├───────────────────┼──────────────────────────────────────┤
│  🔬 Data Quality  │  🔎 Retrieval                        │
│  Completeness: X% │  RAG query success: Y%               │
│  Null ratio: Z%   │  Avg chunks retrieved: N             │
├───────────────────┴──────────────────────────────────────┤
│  📊 Health Score: [██████████] 85/100                    │  ← progress bar + score
└──────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Run button | `st.button("▶ Run Full Evaluation", type="primary")` |
| Metric panels | 4 `st.columns(2)` panels with `st.metric()` inside |
| Score bar | `st.progress(score/100)` + `st.metric("Health Score", f"{score}/100")` |
| Spinners | `st.spinner("Running evaluation...")` per dimension |

---

## Tab 5 — 🌍 External Connectors

```
┌────────────────────────┬────────────────────────────────┐
│  🐝 Kaggle             │  🐙 GitHub                     │
│  Dataset URL input     │  Raw file / repo URL input     │
│  [⬇ Download]          │  [⬇ Import]                    │
└────────────────────────┴────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Layout | `st.columns(2)` side-by-side |
| URL inputs | `st.text_input("Kaggle Dataset URL")` / `st.text_input("GitHub URL")` |
| Action buttons | `st.button("⬇ Download from Kaggle")` / `st.button("⬇ Import from GitHub")` |
| Status | `st.progress()` + `st.success()` / `st.error()` |

---

## Color Usage Summary

| Element | Colour |
|---|---|
| Upload success | `#2ecc71` (green) |
| Upload error | `#e74c3c` (red) |
| Admin-only buttons | Standard secondary grey |
| Graph node labels | Auto palette (distinct per label type) |
| Health score ≥70 | Green progress bar |
| Health score 40–69 | Orange progress bar |
| Health score <40 | Red progress bar |
