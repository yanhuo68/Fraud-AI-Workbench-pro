# 🏗️ Sentinel Fraud AI Workbench: Technical Design

This document outlines the architectural blueprint, data strategies, and AI reasoning frameworks that power the **Sentinel Fraud AI Workbench**.

## 📍 System Overview
Sentinel is a multi-tier AI platform designed for high-stakes fraud investigation. It integrates structured financial data (SQL), network connection data (Graph), and unstructured evidence (Multimodal RAG) into a unified investigative workspace.

## 📑 Design Sections

1.  **[01. Infrastructure Design](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/01_infrastructure.md)**: Docker orchestration, network architecture, and storage strategy (Dual-Process/Triple-Storage).
2.  **[02. Data Flow Architecture](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/02_data_flow.md)**: End-to-end journey of data from ingestion to agentic retrieval and auditing.
3.  **[03. Multi-Agent Intelligence](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/03_multi_agent_system.md)**: Collaborative workflows between Planner, Validator, and Synthesis agents.
4.  **[04. Deep RAG Architectures](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/04_rag_architectures.md)**: Technical deep-dive into SQL RAG, Graph RAG, and Multimodal RAG pipelines.
5.  **[05. API & Integration](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/05_api_and_integration.md)**: FastAPI contract design, JWT authentication, and technical service hooks.
6.  **[06. ML & LLM Forge](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/06_ml_and_llm.md)**: Auto-ML workflows (Scikit-learn) and Generative AI adaptation (LoRA/Fine-Tuning).
7.  **[07. Security & Governance](file:///Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/design/07_security_governance.md)**: RBAC enforcement, forensic audit logging, and AI safety protocols.

---
> [!NOTE]
> This design documentation is intended for engineers and architects maintaining the Sentinel platform. For usage instructions, refer to the **[User Manual](../USER_MANUAL.md)**.
