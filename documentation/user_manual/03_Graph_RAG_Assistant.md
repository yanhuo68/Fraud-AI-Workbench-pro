# 🕸️ Graph RAG Assistant — User Manual

**Page:** Graph RAG Assistant (`pages/3_🕸️_Graph_RAG_Assistant.py`)  
**Access Level:** Authenticated Users

---

## Overview

The **Graph RAG Assistant** enables fraud investigators to explore entity relationships, detect fraud rings, and uncover hidden connections using the Neo4j graph database. Ask questions in plain English — the system generates and executes Cypher queries automatically.

---

## Interface Layout

```
┌──────────────────┬──────────────────────────────────────┐
│ Sidebar           │ Chat history + query results         │
│ - LLM selector    │ Cypher query (expandable)            │
│ - Investigation   │ Results table / graph data           │
│   angles          │ Export controls                      │
└──────────────────┴──────────────────────────────────────┘
```

---

## Step-by-Step Usage

### Step 1 — Choose Your LLM

Select the language model in the sidebar. Options include:
- OpenAI (gpt-4o, gpt-4o-mini)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini 1.5 Pro)
- Local Ollama (Llama3, Mistral)

### Step 2 — Get Investigation Angles *(Optional)*

Click **🧠 Suggest Investigation Angles** to let the AI propose 5 investigation directions based on the current graph schema. Click any suggestion to pre-fill the chat input.

### Step 3 — Ask a Question

Type a natural-language question in the chat input, for example:
- *"Who are the key influencers in the fraud network?"*
- *"Find all accounts connected to flagged merchants."*
- *"Show customers who share the same device ID."*
- *"What is the shortest path between customer A and merchant B?"*

### Step 4 — Review Results

The assistant returns:
1. The **generated Cypher query** (expandable code block).
2. A **results table** or graph JSON.
3. An **AI narrative** interpreting the findings.

---

## Key Features

### Schema Awareness

The assistant loads the current graph schema (node labels, relationship types, property keys) before generating Cypher. This ensures correct syntax and avoids referencing non-existent labels.

### GDS Graph Projections

For advanced queries (centrality, community detection), the assistant can project nodes and relationships into an **in-memory GDS graph**. This enables:
- PageRank centrality
- Betweenness centrality
- Louvain community detection

### PDF Investigation Reports

Click **📄 Export PDF Report** to generate a board-ready PDF containing:
- Cypher query used
- Tabular results
- AI-generated narrative
- Timestamp and metadata

---

## Sidebar Options

| Option | Description |
|---|---|
| **LLM** | Language model for Cypher generation |
| **Suggest Angles** | AI-generated investigation questions |
| **Max Results** | Limit the number of returned nodes/rows |
| **Refresh Schema** | Force re-load of graph schema context |

---

## Example Investigations

| Question | What It Finds |
|---|---|
| "Who are the top 5 by PageRank?" | Most influential nodes in the network |
| "Find all paths between X and Y" | Hidden connection chains |
| "Which merchants appear in multiple fraud cases?" | Repeat offender merchants |
| "Who transacted more than $10,000 in one day?" | High-value anomaly accounts |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| "Neo4j not reachable" | Ensure the Neo4j container is running. Check `NEO4J_SETUP.md`. |
| Empty results | No data has been projected to the graph yet. Use Data Hub → **Project SQL → Graph**. |
| Cypher syntax error | Click **Refresh Schema** in the sidebar and retry. |
| Slow query | Reduce **Max Results** or switch to a lighter LLM. |
