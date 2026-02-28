# 🕒 SESSION_CONTEXT: Fraud Detection AI Workbench
**Date**: 2026-01-25
**Current Status**: Complete Documentation & Rebranding Phase

## 🎯 Project Overview
- **New Name**: `Fraud_Investigation_Workbench-pro`
- **Purpose**: Multi-agent, RAG-powered fraud detection platform.
- **Tech Stack**: Streamlit (Frontend), FastAPI (Backend), Neo4j (Graph), SQLite (SQL), FAISS (Vector).

## ✅ Completed Tasks
1.  **User Manual**: Created a 10-module manual in `Docs/manual/` and indexed in `Docs/USER_MANUAL.md`.
2.  **Technical Design Docs**: Created 7 technical blueprints in `Docs/design/` (Infrastructure, Data Flow, Agents, RAG, API/ML, Security).
3.  **Startup Guide overhaul**:
    - Removed all absolute paths (e.g., `/Users/yanhuo68/...`).
    - Created `.env.example`.
    - Added database initialization steps for transactions and users.
4.  **Global Rename**: Rebranded the UI, sidebar, settings, and all documentation to `Fraud_Investigation_Workbench-pro`.

## 📂 Key Files to Review in New Workspace
- **[STARTUP_GUIDE.md](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/STARTUP_GUIDE.md)**: Portable setup instructions.
- **[.env.example](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/.env.example)**: Reference for configuration.
- **[app.py](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/app.py)** / **[sidebar.py](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/components/sidebar.py)**: UI branding points.
- **[DESIGN_DOC.md](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/DESIGN_DOC.md)**: Main technical entry point.

## 🚀 Next Steps (Verification)
- [ ] Verify `docker-compose.yml` mounts inside the new folder.
- [ ] Ensure `.env` paths (if any) are updated to the new directory name.
- [ ] Confirm all internal links in `Docs/` works correctly with the new structure.

---
> [!NOTE]
> This file serves as a memory bridge for the technical assistant when reopening the project in the new `Fraud-AI-Workbench-pro` directory.
