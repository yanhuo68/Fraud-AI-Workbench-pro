# 📚 Sentinel Pro — Documentation Index

**Project:** Fraud Investigation Workbench Pro  
**Last Updated:** 2026-02-22

---

## 📂 Documentation Directory Structure

```
documentation/
├── README.md                    ← This index
├── references/                  ← Technical & operational reference docs
│   ├── CONFIGURATION_GUIDE.md
│   ├── DEPENDENCY_REFERENCE.md
│   ├── NEO4J_SETUP.md
│   ├── SESSION_CONTEXT.md
│   └── STARTUP_GUIDE.md
├── user_manual/                 ← Per-page user manuals (11 pages)
│   ├── README.md
│   ├── 10_Sidebar.md
│   ├── 00_Home_Dashboard.md
│   ├── 01_Data_Hub.md
│   ├── 02_SQL_RAG_Assistant.md
│   ├── 03_Graph_RAG_Assistant.md
│   ├── 04_Multimodal_RAG_Assistant.md
│   ├── 05_Trends_and_Insights.md
│   ├── 06_ML_Workflow.md
│   ├── 07_LLM_Fine_Tuning_Forge.md
│   ├── 08_API_Integration_Hub.md
│   └── 09_Admin_Console.md
└── ui_design/                   ← Per-page UI design specs (13 files)
    ├── README.md
    ├── 00_Design_System.md
    ├── 01_Sidebar.md
    ├── 02_Home_Dashboard.md
    ├── 03_Data_Hub.md
    ├── 04_SQL_RAG_Assistant.md
    ├── 05_Graph_RAG_Assistant.md
    ├── 06_Multimodal_RAG_Assistant.md
    ├── 07_Trends_and_Insights.md
    ├── 08_ML_Workflow.md
    ├── 09_LLM_Fine_Tuning.md
    ├── 10_API_Integration_Hub.md
    └── 11_Admin_Console.md
```

---

## 📋 Document Reference

### 📦 Technical Reference (`references/`)

| Document | Purpose | Audience |
|---|---|---|
| [CONFIGURATION_GUIDE.md](./references/CONFIGURATION_GUIDE.md) | Every `settings.py` field, env var, Docker config | Developers / Operators |
| [DEPENDENCY_REFERENCE.md](./references/DEPENDENCY_REFERENCE.md) | All 101 Python packages — role, source files, initial config | Developers / DevOps |
| [NEO4J_SETUP.md](./references/NEO4J_SETUP.md) | Neo4j graph database setup and configuration | Developers / DevOps |
| [SESSION_CONTEXT.md](./references/SESSION_CONTEXT.md) | Session context and state management reference | Developers |
| [STARTUP_GUIDE.md](./references/STARTUP_GUIDE.md) | Quick startup guide for the application | All users |

### 📖 User Documentation (`user_manual/`)

| Document | Purpose | Audience |
|---|---|---|
| [user_manual/README.md](./user_manual/README.md) | Master manual index + role permissions + quick-start guide | All users |
| [user_manual/10_Sidebar.md](./user_manual/10_Sidebar.md) | Sidebar auth, nav, LLM selector, Quick Install | All users |
| [user_manual/00_Home_Dashboard.md](./user_manual/00_Home_Dashboard.md) | Home page features | All users |
| [user_manual/01_Data_Hub.md](./user_manual/01_Data_Hub.md) | Upload, explore, graph, evaluate data | Authenticated |
| [user_manual/02_SQL_RAG_Assistant.md](./user_manual/02_SQL_RAG_Assistant.md) | Natural language SQL queries | Authenticated |
| [user_manual/03_Graph_RAG_Assistant.md](./user_manual/03_Graph_RAG_Assistant.md) | Graph network intelligence | Authenticated |
| [user_manual/04_Multimodal_RAG_Assistant.md](./user_manual/04_Multimodal_RAG_Assistant.md) | Evidence file chat (images, audio, PDF, video) | Authenticated |
| [user_manual/05_Trends_and_Insights.md](./user_manual/05_Trends_and_Insights.md) | EDA, anomaly detection, smart join | Authenticated |
| [user_manual/06_ML_Workflow.md](./user_manual/06_ML_Workflow.md) | Model training, SHAP, deployment | data_scientist / admin |
| [user_manual/07_LLM_Fine_Tuning_Forge.md](./user_manual/07_LLM_Fine_Tuning_Forge.md) | LoRA fine-tuning, compare, checkpoints | data_scientist / admin |
| [user_manual/08_API_Integration_Hub.md](./user_manual/08_API_Integration_Hub.md) | All 33 API endpoints, live testing | Authenticated |
| [user_manual/09_Admin_Console.md](./user_manual/09_Admin_Console.md) | Users, roles, SMTP, API keys, onboarding | admin only |

### 🎨 UI Design Documentation (`ui_design/`)

| Document | Covers | Audience |
|---|---|---|
| [ui_design/README.md](./ui_design/README.md) | Design system overview + common patterns | Designers / Developers |
| [ui_design/00_Design_System.md](./ui_design/00_Design_System.md) | Global palette, typography, components, CSS | Designers / Developers |
| [ui_design/01_Sidebar.md](./ui_design/01_Sidebar.md) | Sidebar layout wireframe, all states | Designers / Developers |
| [ui_design/02-11_*.md](./ui_design/) | Per-page wireframes, element specs, colour refs | Designers / Developers |

---

## 🚀 Quick Start for New Developers

1. **Set up environment:** Copy `.env.example` to `.env` and fill in API keys — see [CONFIGURATION_GUIDE.md](./references/CONFIGURATION_GUIDE.md#environment-variable-quick-reference)
2. **Understand dependencies:** Check [DEPENDENCY_REFERENCE.md](./references/DEPENDENCY_REFERENCE.md) before adding new packages
3. **Run the stack:** `docker compose -f docker-compose.neo4j.yml up -d && docker compose up --build`
4. **Install demo data:** Open `http://localhost:8504` → click ⚡ Quick Install Demo Data
5. **Read the manuals:** Start with [user_manual/README.md](./user_manual/README.md) for feature overview
