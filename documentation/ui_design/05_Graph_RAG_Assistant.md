# 🕸️ Graph RAG Assistant — UI Design Specification

**Page:** `pages/3_🕸️_Graph_RAG_Assistant.py`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌────────────────────┬─────────────────────────────────────────────┐
│   SIDEBAR EXTRAS   │  🕸️ Graph RAG Assistant       [st.title]   │
│                    │  "Neo4j fraud network..."    [st.caption]   │
│  [LLM ▾]           ├─────────────────────────────────────────────┤
│  [Max Results ─●─] │                                             │
│  [🔄 Refresh Schema│  [Chat message history (scrollable)]        │
│  [🧠 Suggest Angles│  ┌──────────────────────────────────────┐  │
│                    │  │ 👤 "Who are the top influencers?"     │  │
│  ── Investigation ─│  │ 🤖 Cypher generated + executed       │  │
│  Angles:           │  │ [Cypher code block — expandable]     │  │
│  • Angle 1         │  │ [Results table]                      │  │
│  • Angle 2         │  │ [AI narrative paragraph]             │  │
│  • Angle 3         │  │ [📄 Export PDF]                      │  │
│  • Angle 4         │  └──────────────────────────────────────┘  │
│  • Angle 5         │                                             │
└────────────────────┼─────────────────────────────────────────────┤
                     │  [st.chat_input "Ask about the fraud graph"]│
                     └─────────────────────────────────────────────┘
```

---

## Sidebar Controls

| Element | Spec |
|---|---|
| LLM dropdown | `st.selectbox("LLM", available_llms)` |
| Max results slider | `st.slider("Max Results", 10, 500, 100)` |
| Refresh schema button | `st.button("🔄 Refresh Schema")` |
| Suggest angles button | `st.button("🧠 Suggest Investigation Angles")` |
| Angles list | 5 `st.button(angle_text)` pills — click pre-fills chat input |

### Investigation Angles Panel
```
── 🔍 Investigation Angles ──
• Who are the top fraud ring leaders by PageRank?
• Find all paths between Account X and Merchant Y.
• Which entities appear in multiple fraud cases?
• Show customers with anomalous transaction velocity.
• Identify clusters using Louvain community detection.
```

---

## Chat Message Area

| Message Type | Render |
|---|---|
| User question | `st.chat_message("user")` |
| AI answer — Cypher | `st.expander("🔍 Generated Cypher")` → `st.code(cypher, language="cypher")` |
| AI answer — Results | `st.dataframe(results_df, use_container_width=True)` or JSON display |
| AI narrative | `st.markdown(narrative_text)` — prose paragraph below results |
| PDF export | `st.download_button("📄 Export PDF Report", pdf_bytes)` |
| Neo4j error | `st.error("Neo4j error: ...")` with troubleshooting hint |

---

## Cypher Code Block Style

```
┌──────────────────────────────────────────────────────────┐
│  🔍 Generated Cypher  [▾ expand]                         │
│  ──────────────────────────────────────────────────────  │
│  MATCH (n:Account)-[:TRANSACTED_WITH]->(m:Merchant)      │
│  WHERE m.flagged = true                                  │
│  RETURN n, m LIMIT 100                                   │
└──────────────────────────────────────────────────────────┘
```

Syntax highlighting: `language="cypher"` or `language="text"` fallback.

---

## Result Display Variants

### Tabular Results
`st.dataframe()` — sortable, full-width, max 500 rows displayed.

### Graph JSON / Node List
When results are node objects:
```
st.json(results_dict)
```

### Narrative Text
`st.markdown()` block with:
- Bold entity names
- Bullet points for key findings
- Italic risk level assessment

---

## PDF Export Button

Inline download button appearing after each successful query response:

```
[📄 Export Investigation Report as PDF]
```

`st.download_button()` — styled as secondary button, triggers PDF generation via `POST /reports/generate`.

---

## Error States

| Error | Display |
|---|---|
| Neo4j unreachable | `st.error("❌ Neo4j connection failed. Check container status.")` + link to `NEO4J_SETUP.md` |
| Empty graph | `st.warning("Graph store is empty. Project SQL data first via Data Hub.")` |
| Cypher syntax error | `st.error("Cypher error: ...")` + `Retry with refreshed schema` button |
| Schema stale | Auto-refresh toast: `st.toast("🔄 Schema refreshed", icon="📡")` |

---

## Colour Reference

| Element | Colour |
|---|---|
| Cypher keyword highlight | Blue (via code block) |
| Graph node — Account | `#3498db` |
| Graph node — Merchant | `#e74c3c` |
| Graph node — Transaction | `#2ecc71` |
| Graph node — Document | `#f39c12` |
| PageRank top nodes | Gold border overlay |
