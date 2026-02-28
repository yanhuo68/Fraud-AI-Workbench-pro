# Testing Guide: Fraud Investigation AI Workbench Suite 🧪

This project includes comprehensive test suites across all workbench implementations to ensure data integrity, AI accuracy, and security.

---

## 🚀 Quick Start: Running Tests

### Prerequisites
- **Python 3.11+**
- **Dependencies**: `pip install -r requirements.txt` (Run within the specific workbench folder).
- **API Keys**: Ensure a `.env` file exists with `OPENAI_API_KEY` to run LLM-reliant tests.

### Execution Commands
Navigate to any workbench directory and run:

```bash
# Run all tests in the current workbench
pytest

# Run tests with detailed output
pytest -v

# Run a specific test file
pytest tests/security_tests.py
```

---

## 📂 Test Script Reference

### 🛡️ Basic Workbench (`basic/`)
| Script | Description |
| :--- | :--- |
| `security_tests.py` | Validates SQL injection prevention and ensures sensitive keys are masked in logs. |
| `loaddata_test.py` | Verifies that CSV files are correctly parsed and ingested into the SQLite database. |
| `test_data_prep.py` | Tests the ML pipeline (scaling, encoding, and train/test splitting). |
| `test_rag_sql.py` | Unit tests for natural language to SQL translation logic. |
| `test_langgraph_flow_integration.py` | Full integration test for the multi-step agentic investigation flow. |

### ➕ Plus Workbench (`plus/`)
| Script | Description |
| :--- | :--- |
| `test_erd_and_graphs.py` | Verifies the generation of Mermaid diagrams and PNG schema exports. |
| `test_media_transcription.py` | Tests the audio/video processing and transcription capabilities. |
| `test_pdf_ingestion.py` | Ensures document context is correctly extracted from PDF files for the KB. |
| `test_ml_dashboard.py` | Tests the dynamic metric calculations and visualization logic. |
| `test_auto_import.py` | Verifies the "Cold Start" auto-import logic for new datasets. |

### 🚀 Pro Workbench (`pro/`)
| Category | Description |
| :--- | :--- |
| **Unit Tests** | Focused tests for individual agents (Planner, Critic) and the `version_manager`. |
| **Integration Tests** | Validates the FastAPI backend, including API authentication and ingest endpoints. |
| **Ad-Hoc** | Scripts to verify specific library integrations like `sqlparse` and `moviepy`. |

### 🌌 Plus-Max Workbench (`plus-max/`)
| Script | Description |
| :--- | :--- |
| `test_graph_rag_unit.py` | Tests the advanced hybrid retrieval system (TF-IDF + Vector Embeddings). |
| `test_erd_generator.py` | Verifies the complex multi-table relationship mapping unique to the Max version. |

---

## 🛡️ Security Testing Protocols
1. **SQL Injection**: We use `security_tests.py` to attempt common injection attacks against the RAG pipeline.
2. **PII Masking**: The `SensitiveDataFilter` is tested to ensure no API keys or PII are leaked into `app.log`.
3. **Environment Isolation**: Workspace tests use `pytest-monkeypatch` and `tmp_path` to ensure local data is never modified during test execution.

---
*Maintained for standard Forensic AI verification workflows.*
