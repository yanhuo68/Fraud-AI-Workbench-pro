# 🏠 Home Page — User Manual

**Page:** Home / Dashboard (`app.py`)  
**Access Level:** Public (Guest + All Authenticated Users)

---

## Overview

The **Home page** is the central hub of the Sentinel Fraud Detection AI Workbench. It provides a live platform status overview, quick navigation to all intelligence modules, an AI-powered operator chat assistant, and platform architecture reference.

---

## Sections

### 1. Hero Banner

Displays the platform name, edition (Pro), and a one-line description of the system's capabilities. This section is purely informational.

---

### 2. Guest Promo Banner *(visible when not logged in)*

If you are not logged in, a green banner appears at the top of the page:

> **⚡ Get Started in 30 Seconds**

**What to do:**
- Click **⚡ Quick Install Demo Data** in the sidebar to auto-create demo accounts, load sample fraud datasets, and set up the full environment in one click.
- After installation, log in as `yanhuo68` / `yanhuo68ottawa` (admin account).

---

### 3. 📊 Live Platform Stats

Six real-time metric cards display the current state of the system:

| Metric | Description |
|---|---|
| 🗄️ SQL Tables | Number of active tables in the SQLite database |
| 📄 Uploaded Files | Number of documents indexed in the Knowledge Base |
| 👥 Registered Users | Total user accounts in the platform |
| ⚡ Demo Data | Whether demo seed data has been installed (`✅ Installed` / `⏳ Pending`) |
| 📧 Email Mode | `SMTP ✅` if real email is configured, `Mock 📋` otherwise |
| 🔒 Auth | Authentication method (always `JWT + BCrypt`) |

---

### 4. 🚀 Intelligence Modules

A grid of cards linking to each platform page. Each card shows:
- Module name and description
- A **"Open [Module]"** link to navigate directly to the page
- A **👁 Preview** popover listing key features

**Available Modules:**

| Card | Page |
|---|---|
| 📁 Data Hub | Upload data, manage graph/KB, view evaluations |
| 🧠 SQL RAG Assistant | Natural-language SQL queries |
| 🕸️ Graph RAG Assistant | Neo4j fraud investigation |
| 🎥 Multimodal RAG Assistant | Chat with images, PDFs, audio |
| 📈 Trends & Insights | EDA, anomaly detection, PDF reports |
| 🔄 ML Workflow | Train/evaluate fraud detection models |
| 🧬 LLM Fine-Tuning Forge | Fine-tune Llama/Mistral on fraud data |
| 🔌 API Integration Hub | Live REST API testing |
| 🛡️ Admin Console | *(admin only)* Full platform administration |

---

### 5. 💬 Sentinel Operator Chat

An AI-powered chat assistant that answers questions about the platform.

**How to use:**
1. Type your question in the chat input field at the bottom of the right panel.
2. The assistant answers in real time using the platform's `AppGuideAgent`.
3. Click **🗑 Clear Chat** to reset the conversation history.

**Example questions:**
- *"How do I load demo data?"*
- *"What LLMs are supported?"*
- *"How does the Graph RAG assistant work?"*

---

### 6. 🚦 Quick-Start Guide

An expandable accordion on the right panel. Contains a step-by-step walkthrough:

| Step | Action |
|---|---|
| 0 | Quick Install (first-time setup) |
| 1 | Load data via Data Hub |
| 2 | Query SQL with natural language |
| 3 | Explore fraud network in Graph RAG |
| 4 | Visualize and evaluate graph store |
| 5 | Train a fraud classifier |
| 6 | Chat with physical evidence (Multimodal) |
| 7 | Configure the platform as admin |

---

### 7. 🗺️ Platform Architecture Table

A reference table at the bottom of the right panel summarizing the technology stack:

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI + Uvicorn |
| SQL Store | SQLite |
| Graph Store | Neo4j |
| Vector KB | FAISS + HuggingFace |
| LLM Engine | Ollama · OpenAI · Anthropic · Google |
| Auth | JWT · BCrypt · RBAC |
| Onboarding | One-click demo installer |
| Email | SMTP (configurable / mock) |
| Container | Docker Compose |

---

## Tips

- The **Stats bar** refreshes every time the page loads — use it to confirm data was loaded correctly.
- If you are an admin, the **🛡️ Admin Console** card appears after the standard module grid.
- The **🔧 Role / Permissions** debug line at the bottom shows your current role (only when logged in).
