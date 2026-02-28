# 🛡️ Sentinel Pro — User Manual Index

**Platform:** Fraud Detection AI Workbench · Pro Edition  
**Version:** 2026.02  
**Maintained by:** Platform Administrator

---

## Quick Navigation

| # | Page | Manual | Access Level |
|---|---|---|---|
| — | 🗂️ Sidebar (global component) | [10_Sidebar.md](./10_Sidebar.md) | All users |
| 0 | 🏠 Home / Dashboard | [00_Home_Dashboard.md](./00_Home_Dashboard.md) | All users |
| 1 | 📁 Data Hub | [01_Data_Hub.md](./01_Data_Hub.md) | Authenticated |
| 2 | 🧠 SQL RAG Assistant | [02_SQL_RAG_Assistant.md](./02_SQL_RAG_Assistant.md) | Authenticated |
| 3 | 🕸️ Graph RAG Assistant | [03_Graph_RAG_Assistant.md](./03_Graph_RAG_Assistant.md) | Authenticated |
| 4 | 🎥 Multimodal RAG Assistant | [04_Multimodal_RAG_Assistant.md](./04_Multimodal_RAG_Assistant.md) | Authenticated |
| 5 | 📈 Trends & Insights | [05_Trends_and_Insights.md](./05_Trends_and_Insights.md) | Authenticated |
| 6 | 🔄 ML Workflow | [06_ML_Workflow.md](./06_ML_Workflow.md) | data_scientist / admin |
| 7 | 🧬 LLM Fine-Tuning Forge | [07_LLM_Fine_Tuning_Forge.md](./07_LLM_Fine_Tuning_Forge.md) | data_scientist / admin |
| 8 | 🔌 API Integration Hub | [08_API_Integration_Hub.md](./08_API_Integration_Hub.md) | Authenticated |
| 9 | 🛡️ Admin Console | [09_Admin_Console.md](./09_Admin_Console.md) | admin only |

---

## Role Permissions Summary

| Role | Home | Data Hub | SQL RAG | Graph RAG | Multimodal | Trends | ML | Fine-Tune | API Hub | Admin |
|---|---|---|---|---|---|---|---|---|---|---|
| **guest** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **data_scientist** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

> Roles and page permissions are fully configurable via **Admin Console → Role Management**.

---

## First-Time Setup (Quick Start)

### Option A — One-Click Demo Install *(recommended for new users)*

1. Open the platform — you will see the Home page.
2. In the sidebar, click **⚡ Quick Install Demo Data**.
3. The installer automatically:
   - Creates 3 demo user accounts
   - Executes 5 SQL seed scripts
   - Uploads 2 fraud CSV datasets
4. After install, log in as:
   - **Admin:** `yanhuo68` / `yanhuo68ottawa`
   - **Analyst:** `david@ontario` / `david2026`
   - **Guest:** `stephane@qubec` / `stephane2026`

### Option B — Manual Setup *(for production deployments)*

1. **Register** an admin account via the Login sidebar or `POST /auth/register`.
2. Go to **Admin Console → API Keys** and add your LLM provider key (OpenAI, Anthropic, etc.).
3. Go to **Data Hub → Upload** and upload your CSV files.
4. Go to **Data Hub → Graph Visualizer** and click **Project SQL → Graph**.
5. Begin investigation using SQL RAG, Graph RAG, or Multimodal RAG.

---

## Supported LLM Providers

| Provider | Model Examples |
|---|---|
| OpenAI | gpt-4o, gpt-4o-mini |
| Anthropic | claude-3-5-sonnet-20241022 |
| Google | gemini-1.5-pro, gemini-1.5-flash |
| DeepSeek | deepseek-chat |
| Ollama (local) | llama3, mistral, qwen2.5, phi4 |

---

## Complete API Endpoint Reference

A full list of all 33 API endpoints is documented in the **[API Integration Hub manual](./08_API_Integration_Hub.md)** and is also available interactively in the **🔌 API Integration Hub → Health tab → Complete API Reference table**.

---

## Support & Troubleshooting

| Issue | First Step |
|---|---|
| Page shows "Authentication Required" | Login via the sidebar or use Quick Install |
| SQL RAG returns no results | Upload CSV data via Data Hub first |
| Graph RAG returns empty graph | Run **Project SQL → Graph** in Data Hub |
| LLM not responding | Check API key in Admin Console → API Keys |
| Email not delivered | Configure SMTP in Admin Console → SMTP Settings |
| Neo4j unreachable | Check Docker container status: `docker compose ps` |
| Demo install failed | Admin Console → Onboarding Settings → Reset & Re-run |
