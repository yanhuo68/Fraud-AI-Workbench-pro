# 📁 Data Hub — User Manual

**Page:** Data Hub (`pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)`)  
**Access Level:** Authenticated Users (some operations require Admin)

---

## Overview

The **Data Hub** is the primary data ingestion and management center. It handles file uploads (CSV, PDF, images, audio, video), runs SQL seed scripts, visualizes the Neo4j graph, evaluates graph quality, and connects to external data sources such as Kaggle and GitHub.

---

## Tabs

### Tab 1 — 📤 Upload Files

Upload data files to seed the system.

**Supported file types:**

| Extension | Processing |
|---|---|
| `.csv` | Imported as a new SQL table + graph node created |
| `.pdf` | Text extracted → Knowledge Base + Graph |
| `.png` / `.jpg` / `.jpeg` | Image analysed → Knowledge Base + Graph |
| `.mp3` / `.wav` | Audio transcribed → Knowledge Base + Graph |
| `.mp4` | Frames + transcript extracted → Knowledge Base + Graph |
| `.sql` | Script executed against SQLite database |

**Steps:**
1. Click **Browse files** or drag and drop your file.
2. Click **⬆️ Upload & Ingest**.
3. The system shows a progress spinner. On success, you see a summary of what was created (table name, row count, etc.).

> **Note:** CSV files automatically create a new SQL table named after the file. If a table with the same name exists, it will be replaced.

---

### Tab 2 — 🗄️ Database Explorer

Browse all SQL tables currently stored in the database.

**Features:**
- **Table selector dropdown** — pick any loaded table.
- **Data preview** — shows the first 100 rows in a sortable/scrollable table.
- **Row count & column list** displayed as metadata.
- **📥 Download as CSV** button to export any table.

---

### Tab 3 — 🕸️ Graph Visualizer

An interactive physics-based visualization of the Neo4j graph store.

**Controls:**
- 🔍 Zoom in/out using scroll or pinch.
- 🖱 Drag nodes to rearrange the layout.
- 🖱 Hover a node to see its label and properties in a tooltip.
- Use the **depth slider** to control how many hops to render from seed nodes.

**Node types shown:**
- `Document` — uploaded files
- `Table` — SQL tables
- `Column` — table columns
- `Entity` — extracted fraud-relevant entities
- `Person`, `Account`, `Merchant`, `Transaction` — domain nodes (when projected)

**Buttons:**
- **▶ Load Graph** — fetches and renders the current graph state.
- **🔄 Rebuild Graph** *(admin)* — rebuilds from all uploaded files.
- **📤 Project SQL → Graph** *(admin)* — projects SQL table rows as graph nodes.

---

### Tab 4 — 🔬 Graph Database Evaluation

Run a comprehensive quality assessment of the Neo4j graph store.

**How to use:**
1. Click **▶ Run Full Evaluation**.
2. The system probes multiple dimensions and returns a health score (0–100).

**Evaluation dimensions:**

| Panel | What's Measured |
|---|---|
| 🏥 Connectivity | Node count, relationship count, orphan nodes |
| ⚡ Performance | Query latency, index usage |
| 🔬 Quality | Node property completeness, null ratios |
| 🔎 Retrieval | Sample RAG query success rate |

---

### Tab 5 — 🌍 External Connectors

Connect to external data sources to import datasets directly.

#### Kaggle Connector
1. Enter your **Kaggle dataset URL** (e.g. `kaggle.com/datasets/user/dataset-name`).
2. Ensure your Kaggle API credentials are configured in **Admin Console → External Credentials**.
3. Click **⬇ Download from Kaggle** — the dataset is downloaded and ingested automatically.

#### GitHub Connector
1. Enter a **GitHub raw file URL** or repository URL.
2. Ensure your GitHub token is set in **Admin Console → External Credentials**.
3. Click **⬇ Import from GitHub** — the file is fetched and ingested.

---

## Common Workflows

### Loading Demo Data
If you want to load sample fraud data without uploading files manually, use **⚡ Quick Install Demo Data** from the Home page sidebar (when not logged in) or navigate to **Admin Console → Onboarding Settings** as an admin.

### Rebuilding the Knowledge Base
The Knowledge Base (used by SQL RAG and Multimodal RAG assistants) rebuilds automatically on file upload. To force a manual rebuild:
- Go to the **Upload** tab and upload any file, or
- Use the **Admin Console → rebuild-graph** API endpoint.

---

## Tips

- Large CSV files (>10 MB) may take 15–30 seconds to process.
- The Graph Visualizer is read-only for guest/data_scientist roles unless admin operations are enabled.
- The **📥 Download as CSV** button is always available regardless of role.
