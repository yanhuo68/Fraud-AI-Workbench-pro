# End-to-End Architecture for Fraud Analytics System

This document describes the complete architecture used to process transactions, run ML models, apply RAG, generate SQL, and visualize results.

---

# 1. Data Layer
- Uploaded CSV (user-provided dataset)
- `data/raw/` storage
- SQLite database built from CSV
- Vector store (`FAISS`) for knowledge-base documents

---

# 2. Processing Layer
- Feature engineering (`feature_engineering_guide.md`)
- Preprocessing pipeline
- Balance validation logic
- Fraud rule evaluation

---

# 3. Machine Learning Layer
Models supported:
- Isolation Forest
- Local Outlier Factor
- One-Class SVM
- Random Forest
- Gradient Boosting
- XGBoost (optional)
- Logistic Regression (baseline)
- Future extension: LSTM for sequences

Outputs:
- Probabilities
- Anomaly scores
- Feature importances
- Confusion matrix metrics

---

# 4. RAG Layer (Retrieval-Augmented Generation)
Uses documents:
- fraud_intro
- fraud_risk_rules
- model_interpretation
- fraud_chain_patterns
- ml_evaluation_metrics

Retrieval:  
- FAISS vector store  
- Top-k context selection  

Generation:  
- Local LLM (Ollama)  
- OpenAI GPT-4o  
- DeepSeek R1/V3  

---

# 5. SQL RAG Layer (LangGraph)
Nodes:
- SQL Planner
- SQL Executor
- Critic Agent
- Explanation Agent
- Trace Logging Agent

---

# 6. Agentic AI Layer
Agents:
- Data Q&A Agent
- SQL Planning Agent
- Fraud Explanation Agent
- Model Interpretation Agent
- Risk Scoring Agent
- Policy Agent (safety compliance)

---

# 7. UI (Streamlit)
Tabs:
- ML Dashboard
- SQL RAG Q&A
- LLM Explanation
- Agent Workflow
- Fraud KB Chat
- Model Metrics Dashboard

---

# 8. CI/CD + Testing
- pytest tests for ML + SQL
- Eval flows (LangSmith)
- Regression test suite (`test_cases_suite.md`)

---
