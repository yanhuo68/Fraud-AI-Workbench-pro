# 🧠 SQL RAG Assistant — UI Design Specification

**Page:** `pages/2_🧠_SQL_RAG_Assistant.py`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌────────────────────┬─────────────────────────────────────────────┐
│   SIDEBAR EXTRAS   │  🧠 SQL RAG Assistant        [st.title]     │
│                    │  "Natural-language SQL..."   [st.caption]   │
│  [Table ▾]         ├─────────────────────────────────────────────┤
│  [LLM ▾]           │                                             │
│  [🔄 Refresh Qs]   │  [Chat message history (scrollable)]        │
│  [Show ERD toggle] │  ┌──────────────────────────────────────┐  │
│                    │  │ 👤 User: "Top 10 transactions?"       │  │
│  ── Suggestions ── │  │ 🤖 AI: "Here are the results..."     │  │
│  • Sample Q 1      │  │ [SQL code block]                     │  │
│  • Sample Q 2      │  │ [Results dataframe table]            │  │
│  • Sample Q 3      │  │ [📥 Download CSV]                    │  │
│  • Sample Q 4      │  └──────────────────────────────────────┘  │
│  • Sample Q 5      │                                             │
│                    │  [Security Alert — if triggered]            │
│                    │  🔴 Blocked query display                   │
│                    ├─────────────────────────────────────────────┤
│                    │  [ERD Diagram section — collapsible]        │
│                    ├─────────────────────────────────────────────┤
│                    │  [st.chat_input "Ask a SQL question..."]    │
└────────────────────┴─────────────────────────────────────────────┘
```

---

## Sidebar Controls (within global sidebar)

| Element | Spec |
|---|---|
| Table dropdown | `st.selectbox("Table", all_tables)` |
| LLM dropdown | `st.selectbox("LLM", available_llms)` |
| Refresh button | `st.button("🔄 Refresh Case Study Prompts")` |
| ERD toggle | `st.checkbox("Show ERD")` |
| Sample questions | 5 `st.button(question_text)` pills — click pre-fills chat input |

### Auto-Generated Sample Questions Panel
```
── 💡 Suggested Questions ──
• What are the top 5 highest-value transactions?
• How many transactions occurred in March 2024?
• Which merchants appear most frequently?
• Show the average transaction amount by category.
• Find all transactions flagged as suspicious.
```
Rendered as 5 `st.button()` elements, stacked vertically. Each button text is truncated to ~60 chars.

---

## Chat Message Area

| Message Type | Render |
|---|---|
| User question | `st.chat_message("user")` — right-aligned avatar |
| AI answer | `st.chat_message("assistant")` — left-aligned robot avatar |
| SQL query block | Inside assistant message: `st.expander("🔍 Generated SQL")` → `st.code(sql, language="sql")` |
| Results table | Inside assistant message: `st.dataframe(df, use_container_width=True)` |
| Download | Inside assistant message: `st.download_button("📥 Download CSV", ...)` |
| Error | Inside assistant message: `st.error("Query failed: ...")` |

---

## Security Alert Banner

Shown when blocked query detected:

```
┌──────────────────────────────────────────────────────────┐
│  🔴 Security Alert                                        │
│  ─────────────────────────────────────────────────────   │
│  Blocked SQL pattern detected. Only SELECT statements    │
│  are permitted. The query was not executed.              │
│  Blocked query: [code block]                             │
└──────────────────────────────────────────────────────────┘
```

Rendered as `st.error()` with the blocked query in `st.code()` inside an expander.

---

## ERD Diagram Section

Collapsible `st.expander("📊 Entity Relationship Diagram")`:

```
┌──────────────────────────────────────────────────────────┐
│  Column limit: [───●──────] 20                           │  ← st.slider
│                                                          │
│        [SVG/PNG ERD diagram — auto generated]            │
│        Selected table highlighted in blue                │
│        FK relationships shown as arrows                  │
└──────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Column limit slider | `st.slider("Max columns", 5, 50, 20)` |
| Diagram | `st.image(erd_png, use_column_width=True)` |
| Download | `st.download_button("📥 Download ERD", erd_bytes, "erd.png")` |

---

## Chat Input Bar

```
┌──────────────────────────────────────────────────────────┐
│  💬  Ask a question about your fraud data...     [Send ▶] │
└──────────────────────────────────────────────────────────┘
```

`st.chat_input("Ask a SQL question about your fraud data...")` — pinned to bottom of page.

---

## Colour & State Reference

| State | Visual |
|---|---|
| Query in progress | Spinner inside chat message bubble |
| SELECT success | Green result count badge |
| Security block | Red `st.error()` banner |
| Empty result | `st.info("Query returned 0 rows.")` |
| Table not found | `st.warning("No tables found. Upload data first.")` |

---

## Typography Specifics

| Element | Style |
|---|---|
| SQL code blocks | Monospace, syntax-highlighted (`language="sql"`) |
| Result count | `st.caption("Returned N rows")` |
| Sample question buttons | Truncated at ~60 chars, regular weight |
| ERD section header | Inside expander header |
