# 🧠 SQL RAG Assistant — User Manual

**Page:** SQL RAG Assistant (`pages/2_🧠_SQL_RAG_Assistant.py`)  
**Access Level:** Authenticated Users

---

## Overview

The **SQL RAG Assistant** lets you query your fraud datasets using plain English. It translates natural-language questions into SQL, executes them against the SQLite database, and returns results in a structured table. A security layer prevents injection attacks and blocks non-SELECT statements.

---

## Interface Layout

```
┌─────────────────────────────────────────────────┐
│ Sidebar: Table selector + sample questions        │
├─────────────────────┬───────────────────────────┤
│ Chat input + history│ Results table / ERD        │
└─────────────────────┴───────────────────────────┘
```

---

## Step-by-Step Usage

### Step 1 — Select a Table

Use the **Table** dropdown in the sidebar to choose which SQL table to query.

> **Auto-suggestion:** As soon as you select a table, the system automatically generates 5 contextually relevant sample questions based on the schema. They appear below the dropdown.

### Step 2 — Ask a Question

Type your question in the chat input box at the bottom, for example:

- *"Show me the top 10 transactions by amount."*
- *"How many transactions occurred in March 2024?"*
- *"Find all merchants with more than 50 transactions."*

Alternatively, click one of the **auto-generated sample questions** to pre-fill the input.

### Step 3 — Review Results

- The generated **SQL query** is shown in an expandable code block above the results.
- Results appear as a paginated sortable table.
- Click **📥 Download CSV** to export the result set.

---

## Security Layer

All generated SQL is validated before execution:

| Check | Description |
|---|---|
| **SELECT-only** | Only `SELECT` statements are permitted. `DROP`, `DELETE`, `INSERT`, `UPDATE` are blocked. |
| **WITH clause support** | CTEs (`WITH ... AS (...)`) are correctly parsed and allowed. |
| **Injection prevention** | Parameterised query detection prevents SQL injection patterns. |

If a violation is detected, a **🔴 Security Alert** is shown and the query is not executed.

---

## ERD Diagram

At the bottom of the results panel, an **Entity Relationship Diagram (ERD)** is rendered for the selected table, showing:
- Selected table's columns and types
- Foreign-key relationships to other tables
- A **column limit slider** to reduce diagram size for wide tables

---

## Sidebar Options

| Option | Description |
|---|---|
| **Table** | Active table to query |
| **LLM** | Language model to use for SQL generation |
| **Refresh Sample Questions** | Manually regenerate the 5 suggested questions |
| **Show ERD** | Toggle the ERD diagram visibility |

---

## Sample Questions (Auto-Generated)

When you select a table, 5 questions are generated based on the column names and data types. Examples:

- For a transactions table: *"What are the top 5 highest-value transactions?"*
- For a customers table: *"How many customers registered this year?"*

Click **🔄 Refresh Case Study Prompts** in the sidebar to regenerate new suggestions.

---

## Tips

- Use specific column names in your questions for more accurate SQL generation.
- If results are empty, check whether data has been loaded in the **Data Hub**.
- The **LLM selector** in the sidebar lets you switch between OpenAI, Anthropic, Google, or local Ollama models.
- For complex multi-table queries, try the **Trends & Insights** page instead.
