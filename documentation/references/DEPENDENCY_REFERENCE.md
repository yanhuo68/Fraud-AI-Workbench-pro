# 📦 Dependency Reference

**Project:** Sentinel Fraud Investigation Workbench Pro  
**Source:** `requirements.txt` (101 packages)  
**Python:** 3.11 (CPython, slim-bookworm Docker base)

---

## How to Read This Document

Each dependency entry answers three questions:
1. **Why the system needs it** — functional role in the architecture
2. **Which source files reference it** — where it is imported/used
3. **Initial configuration / notes** — version pin, known constraints, or setup step

---

## Category A — Core Web Application

### `streamlit >= 1.33.0`
| Field | Detail |
|---|---|
| **Role** | Frontend web framework — renders all pages, chat UI, forms, charts, file uploaders |
| **Referenced by** | `app.py`, all `pages/*.py`, `components/sidebar.py` |
| **Configuration** | Port set via `STREAMLIT_SERVER_PORT=8504`; CORS disabled in Dockerfile (`STREAMLIT_SERVER_ENABLECORS=false`); run with `streamlit run app.py --server.port=8504 --server.address=0.0.0.0` |
| **Notes** | Version ≥1.33 required for `st.chat_message`, `st.toggle`, `st.page_link` APIs |

### `altair >= 5.0.0`
| Field | Detail |
|---|---|
| **Role** | Declarative chart library used for EDA charts in Trends & Insights; Streamlit uses Altair internally |
| **Referenced by** | `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)` |
| **Configuration** | No explicit config; driven by Streamlit's Vega-Lite renderer |

---

## Category B — Data Processing

### `pandas >= 2.2.0`
| Field | Detail |
|---|---|
| **Role** | Core data manipulation — loading CSVs, displaying dataframes, computing statistics, joining tables |
| **Referenced by** | Almost every page and agent: `agents/`, `pages/`, `utils/` |
| **Configuration** | No special config; relies on system memory. Docker containers have no memory cap, so large DataFrames may OOM |

### `numpy >= 1.26.0`
| Field | Detail |
|---|---|
| **Role** | Numerical computation — used by scikit-learn, SHAP, FAISS, and pandas under the hood |
| **Referenced by** | `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)`, `agents/ml_agent.py` |
| **Configuration** | Built against BLAS/LAPACK; system deps `libblas-dev liblapack-dev` are installed in both Dockerfiles |

### `pyarrow >= 15.0.0`
| Field | Detail |
|---|---|
| **Role** | Columnar memory format required by pandas 2.x and Streamlit's dataframe rendering engine |
| **Referenced by** | Implicit — Streamlit and pandas import it automatically |
| **Configuration** | None required |

---

## Category C — SQL & Database

### `SQLAlchemy >= 2.0.0`
| Field | Detail |
|---|---|
| **Role** | ORM and SQL engine for SQLite — used by the FastAPI backend to manage the `rag.db` database (users, roles, uploads metadata) |
| **Referenced by** | `api/database.py`, `api/routers/auth.py`, `api/routers/admin.py`, `api/routers/ingest.py` |
| **Configuration** | `DB_PATH` env var (default `data/db/rag.db`) passed into `create_engine("sqlite:///...")` |

### `duckdb >= 0.10.2`
| Field | Detail |
|---|---|
| **Role** | In-process analytical SQL engine — used for complex analytical queries over uploaded CSV files in the SQL RAG flow |
| **Referenced by** | `agents/sql_agent.py`, `pages/2_🧠_SQL_RAG_Assistant.py` |
| **Configuration** | No persistent DB file — DuckDB operates in-memory or against CSV files directly |

### `sqlite-utils >= 3.36.0`
| Field | Detail |
|---|---|
| **Role** | CLI/Python utility for inspecting SQLite databases — used by the SQL RAG agent for schema introspection |
| **Referenced by** | `agents/sql_agent.py`, `utils/db_utils.py` |
| **Configuration** | Targets `settings.db_path` |

### `sqlparse >= 0.4.4`
| Field | Detail |
|---|---|
| **Role** | SQL parsing and validation — extracts SELECT statements from LLM output and detects security-blocked patterns (non-SELECT queries) |
| **Referenced by** | `agents/sql_agent.py`, `pages/2_🧠_SQL_RAG_Assistant.py` |
| **Configuration** | No config — used as a pure function library |

---

## Category D — Machine Learning & Preprocessing

### `scikit-learn >= 1.4.0`
| Field | Detail |
|---|---|
| **Role** | ML model training — RandomForest classifier, preprocessing (StandardScaler, LabelEncoder), train/test split, metrics |
| **Referenced by** | `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)`, `agents/ml_agent.py`, `api/routers/ml.py` |
| **Configuration** | Models saved to `MODEL_DIR` (default `models/`) via `joblib.dump()` |

### `scipy >= 1.12.0`
| Field | Detail |
|---|---|
| **Role** | Statistical functions — used for Z-score anomaly detection in Trends & Insights |
| **Referenced by** | `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)` |
| **Configuration** | Requires BLAS/LAPACK — system deps installed in Dockerfiles |

### `joblib >= 1.3.2`
| Field | Detail |
|---|---|
| **Role** | Model serialization — saves and loads trained ML model files to/from `models/` directory |
| **Referenced by** | `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)`, `api/routers/ml.py` |
| **Configuration** | Model files stored at `{MODEL_DIR}/{model_name}.pkl` |

### `shap >= 0.45.0`
| Field | Detail |
|---|---|
| **Role** | Model explainability — generates SHAP feature importance, beeswarm, and waterfall plots |
| **Referenced by** | `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)` |
| **Configuration** | Requires `numba` for TreeExplainer fast-paths; `numba >= 0.59.0` and `llvmlite >= 0.42.0` must be installed together |

### `numba >= 0.59.0` / `llvmlite >= 0.42.0`
| Field | Detail |
|---|---|
| **Role** | JIT compilation required by SHAP's TreeExplainer for performance |
| **Referenced by** | Implicit — `shap` imports them |
| **Configuration** | Versions must be compatible pair (numba 0.59 ↔ llvmlite 0.42) |

---

## Category E — Vector Store & Embeddings (RAG)

### `faiss-cpu >= 1.8.0`
| Field | Detail |
|---|---|
| **Role** | Vector similarity search — stores and retrieves document chunk embeddings for all RAG pipelines (SQL, Graph, Multimodal) |
| **Referenced by** | `agents/rag_agent.py`, `agents/multimodal_agent.py` |
| **Configuration** | Index files persisted to `KB_DIR` (default `data/kb/`); requires `libblas-dev` in Docker |

### `sentence-transformers >= 2.6.0`
| Field | Detail |
|---|---|
| **Role** | Document embedding model — converts text chunks to vectors for FAISS indexing; default model `all-MiniLM-L6-v2` downloaded from HuggingFace Hub |
| **Referenced by** | `agents/rag_agent.py`, `agents/multimodal_agent.py` |
| **Configuration** | Model downloaded to `~/.cache/huggingface/` on first run; internet access or pre-cached image required |

### `tqdm >= 4.66.0`
| Field | Detail |
|---|---|
| **Role** | Progress bars for embedding/indexing loops |
| **Referenced by** | `agents/rag_agent.py`, ingest utilities |
| **Configuration** | None |

---

## Category F — LLM Clients

### `openai >= 1.14.0`
| Field | Detail |
|---|---|
| **Role** | OpenAI GPT-4o / GPT-4o-mini API client |
| **Referenced by** | `agents/llm_router.py`, `agents/sql_agent.py`, `agents/rag_agent.py` |
| **Configuration** | `OPENAI_API_KEY` env var (`.env` or docker-compose `environment:`) |
| **Initial setup** | `export OPENAI_API_KEY=sk-...` |

### `anthropic >= 0.18.1`
| Field | Detail |
|---|---|
| **Role** | Anthropic Claude 3.5 Sonnet API client |
| **Referenced by** | `agents/llm_router.py` |
| **Configuration** | `ANTHROPIC_API_KEY` env var |

### `transformers >= 4.39.0`
| Field | Detail |
|---|---|
| **Role** | HuggingFace model loading — used for LLM fine-tuning (LoRA/QLoRA) and embedding models |
| **Referenced by** | `pages/9_🧠_LLM_Fine_Tuning.py (wrapper for src/views/llm_fine_tuning/)`, `agents/` |
| **Configuration** | Models cached to `~/.cache/huggingface`; `HUGGINGFACEHUB_API_TOKEN` needed for gated models |

### `huggingface-hub >= 0.21.3`
| Field | Detail |
|---|---|
| **Role** | Downloads models and datasets from HuggingFace Hub |
| **Referenced by** | `transformers`, `sentence-transformers` |
| **Configuration** | Token: `HUGGINGFACEHUB_API_TOKEN` (optional for public models) |

---

## Category G — LangChain Stack

### `langchain >= 0.1.0` + ecosystem
| Package | Role | Referenced by |
|---|---|---|
| `langchain` | Core chains, prompts, agents framework | `agents/sql_agent.py`, `agents/rag_agent.py` |
| `langchain-openai` | OpenAI integration | `agents/llm_router.py` |
| `langchain-google-genai` | Google Gemini integration | `agents/llm_router.py` |
| `langchain-anthropic` | Claude integration | `agents/llm_router.py` |
| `langchain-community` | Community tools (DuckDB, Neo4j, GitHub) | `agents/` |
| `langchain-text-splitters` | Document chunking for RAG | `agents/rag_agent.py` |
| `langgraph >= 0.0.20` | Multi-agent DAG orchestration — the Intelligence pipeline | `agents/graph_pipeline.py`, `api/routers/intelligence.py` |

**Configuration:** Models injected at runtime via `llm_router.get_llm(model_id)` which reads `settings.*_api_key`.

---

## Category H — HTTP & External Integrations

### `httpx >= 0.27.0`
| Field | Detail |
|---|---|
| **Role** | Async HTTP client — used internally by some LLM clients and for Ollama health checks |
| **Referenced by** | `agents/llm_router.py` (Ollama probe) |
| **Configuration** | Ollama base URL: `http://host.docker.internal:11434` (auto-discovered) |

### `requests >= 2.31.0`
| Field | Detail |
|---|---|
| **Role** | Sync HTTP client — used by Streamlit pages to call the FastAPI backend and external services |
| **Referenced by** | `components/sidebar.py`, all `pages/*.py`, `utils/demo_installer.py` |
| **Configuration** | `API_URL` env var consumed by `settings.api_url` |

### `kaggle >= 1.6.0`
| Field | Detail |
|---|---|
| **Role** | Kaggle dataset downloader — used in Data Hub → External Connectors tab |
| **Referenced by** | `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)` |
| **Configuration** | Requires `~/.kaggle/kaggle.json` with `{"username": "...", "key": "..."}` |

### `PyGithub >= 2.1.0`
| Field | Detail |
|---|---|
| **Role** | GitHub file/repo importer — used in Data Hub → External Connectors tab |
| **Referenced by** | `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)` |
| **Configuration** | Optionally pass `GITHUB_TOKEN` for private repos |

---

## Category I — PDF Export

### `reportlab >= 4.0.9` / `fpdf2 >= 2.7.8` / `fpdf == 1.7.2`
| Field | Detail |
|---|---|
| **Role** | PDF generation — Graph RAG and Trends & Insights export investigation reports as PDF |
| **Referenced by** | `api/routers/reports.py`, `agents/report_agent.py` |
| **Configuration** | No config — output is a bytes blob returned to `st.download_button()` |
| **Notes** | Both `fpdf2` (new) and `fpdf==1.7.2` (legacy pin) are listed — `fpdf2` is the active one |

---

## Category J — File Parsing

### `PyPDF2 >= 3.0.0`
| Field | Detail |
|---|---|
| **Role** | PDF text extraction — extracts content from uploaded PDFs for RAG indexing |
| **Referenced by** | `agents/rag_agent.py`, `agents/multimodal_agent.py` |
| **Configuration** | None |

### `python-docx >= 1.1.0`
| Field | Detail |
|---|---|
| **Role** | Word document reading/writing — reads `.docx` uploads and generates reports |
| **Referenced by** | `agents/multimodal_agent.py`, report utilities |
| **Configuration** | None |

### `python-pptx`
| Field | Detail |
|---|---|
| **Role** | PowerPoint file reading — extracts text from `.pptx` uploads for RAG indexing |
| **Referenced by** | `agents/multimodal_agent.py` |
| **Configuration** | None |

### `beautifulsoup4`
| Field | Detail |
|---|---|
| **Role** | HTML parsing — used when parsing web-scraped content or HTML documentation files |
| **Referenced by** | `utils/`, documentation processors |
| **Configuration** | None |

### `moviepy >= 1.0.3`
| Field | Detail |
|---|---|
| **Role** | Audio extraction from video files — extracts MP3 from uploaded MP4/MOV for transcription |
| **Referenced by** | `agents/multimodal_agent.py` |
| **Configuration** | Requires `libgl1 libglib2.0-0` system packages (installed in `Dockerfile.streamlit`) |

---

## Category K — Visualization & EDA

### `streamlit-agraph >= 0.0.45`
| Field | Detail |
|---|---|
| **Role** | Interactive physics graph component — renders Neo4j subgraphs visually in Data Hub → Graph Visualizer |
| **Referenced by** | `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)` |
| **Configuration** | Node/edge config passed as `Config(width, height, physics)` object |

### `graphviz >= 0.20.1`
| Field | Detail |
|---|---|
| **Role** | ERD diagram generation — produces database Entity Relationship Diagram as PNG |
| **Referenced by** | `pages/2_🧠_SQL_RAG_Assistant.py`, `utils/erd_utils.py` |
| **Configuration** | Requires `graphviz` system binary (installed via `apt-get install graphviz`) |

### `pyvis >= 0.3.2`
| Field | Detail |
|---|---|
| **Role** | Alternative interactive graph renderer — fallback for graph visualizations |
| **Referenced by** | `pages/1_��_Data_Hub.py (wrapper for src/views/data_hub/)` |
| **Configuration** | Outputs HTML embedded via `st.components.v1.html()` |

### `matplotlib >= 3.8.2` / `seaborn >= 0.13.2`
| Field | Detail |
|---|---|
| **Role** | SHAP chart rendering (matplotlib backend), EDA heatmaps |
| **Referenced by** | `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)`, `pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)` |
| **Configuration** | Matplotlib backend set to `Agg` (non-interactive) in Docker context |

---

## Category L — JSON / YAML / Data Validation

### `pydantic >= 2.6.0` / `pydantic-settings >= 2.2.0`
| Field | Detail |
|---|---|
| **Role** | Data validation for API request/response models and settings loading from env vars |
| **Referenced by** | `api/models.py`, `config/settings.py` |
| **Configuration** | `Settings` class uses `SettingsConfigDict(env_file=".env")` — reads from `.env` file first, then environment variables |

### `PyYAML >= 6.0.1`
| Field | Detail |
|---|---|
| **Role** | YAML file parsing — used for reading configuration files and LLM fine-tuning dataset specs |
| **Referenced by** | `agents/`, `config/` |
| **Configuration** | None |

---

## Category M — Utilities

### `python-dotenv >= 1.0.0`
| Field | Detail |
|---|---|
| **Role** | Loads `.env` file into environment variables at startup |
| **Referenced by** | `config/settings.py` (via pydantic-settings) |
| **Configuration** | `.env` file must be in project root; variables override docker-compose `environment:` only if not already set |

### `python-dateutil >= 2.9.0`
| Field | Detail |
|---|---|
| **Role** | Date parsing — handles flexible date strings in uploaded datasets |
| **Referenced by** | `agents/sql_agent.py`, `pages/5_📈_Trends_and_Insights.py (wrapper for src/views/trends_insights/)` |
| **Configuration** | None |

### `regex >= 2023.12.25`
| Field | Detail |
|---|---|
| **Role** | Advanced regex — used for SQL extraction from LLM output (WITH clause, comment stripping) |
| **Referenced by** | `agents/sql_agent.py` |
| **Configuration** | None |

### `networkx >= 3.2.1`
| Field | Detail |
|---|---|
| **Role** | Graph data structure — used for PK/FK relationship detection during ERD generation |
| **Referenced by** | `utils/erd_utils.py` |
| **Configuration** | None |

### `markdown >= 3.6` / `pygments >= 2.17.2`
| Field | Detail |
|---|---|
| **Role** | Markdown rendering and syntax highlighting — used in the help documentation viewer embedded in the sidebar |
| **Referenced by** | `components/sidebar.py`, help system |
| **Configuration** | None |

---

## Category N — FastAPI Backend

### `fastapi >= 0.110.0`
| Field | Detail |
|---|---|
| **Role** | REST API framework — exposes all backend endpoints (`/auth`, `/ingest`, `/admin`, `/ml`, `/intelligence`, `/health`, `/reports`, `/keys`) |
| **Referenced by** | `api/main.py`, all `api/routers/*.py` |
| **Configuration** | Host: `API_HOST=0.0.0.0`, Port: `API_PORT=8000`, started via `uvicorn api.main:app` |

### `uvicorn >= 0.29.0`
| Field | Detail |
|---|---|
| **Role** | ASGI server running FastAPI |
| **Referenced by** | `Dockerfile.fastapi` CMD |
| **Configuration** | `CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]` |

### `python-multipart >= 0.0.9`
| Field | Detail |
|---|---|
| **Role** | Multipart form data parsing — required by FastAPI to accept file uploads (`/ingest/file`) and form-encoded login (`/auth/token`) |
| **Referenced by** | `api/routers/ingest.py`, `api/routers/auth.py` |
| **Configuration** | Installed automatically by FastAPI when `python-multipart` is present |

### `passlib[bcrypt] >= 1.7.4`
| Field | Detail |
|---|---|
| **Role** | Password hashing — BCrypt hashes stored in SQLite `users` table |
| **Referenced by** | `api/routers/auth.py`, `utils/auth_utils.py` |
| **Configuration** | Default BCrypt cost factor (12 rounds) |

### `python-jose[cryptography] >= 3.3.0`
| Field | Detail |
|---|---|
| **Role** | JWT creation and validation — signs and verifies access tokens |
| **Referenced by** | `api/routers/auth.py`, `utils/auth_utils.py` |
| **Configuration** | `SECRET_KEY` env var (default `SUPER_SECRET_KEY_REPLACE_ME` — **must be changed in production**), `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=1440` |

---

## Category O — Logging

### `loguru >= 0.7.2`
| Field | Detail |
|---|---|
| **Role** | Structured logging — used across all backend modules for request tracing, error capture, and debug output |
| **Referenced by** | `api/main.py`, all `api/routers/`, `agents/` |
| **Configuration** | `LOG_LEVEL=INFO`, `LOG_FILE=logs/run.log` |

---

## Category P — Graph Database

### `neo4j >= 5.0.0`
| Field | Detail |
|---|---|
| **Role** | Neo4j Python driver — executes Cypher queries against the graph database for Graph RAG, GDS algorithms, and graph evaluation |
| **Referenced by** | `agents/graph_agent.py`, `api/routers/admin.py`, `config/settings.py` (`graph_driver` property) |
| **Configuration** | `GRAPH_STORE_URI=bolt://fraud_neo4j:7687`, `GRAPH_STORE_USER=neo4j`, `GRAPH_STORE_PASSWORD=password` |
| **Initial setup** | Start `docker-compose.neo4j.yml` first: `docker compose -f docker-compose.neo4j.yml up -d` |

---

## System Package Dependencies (apt-get)

| System Package | Required by | Installed in |
|---|---|---|
| `build-essential` | numpy, scipy, FAISS compilation | Both Dockerfiles |
| `libblas-dev` | scipy, numpy (BLAS routines) | `Dockerfile.fastapi` |
| `liblapack-dev` | scipy (linear algebra) | `Dockerfile.fastapi` |
| `libatlas-base-dev` | numpy fallback BLAS | `Dockerfile.fastapi` |
| `gfortran` | scipy Fortran extensions | `Dockerfile.fastapi` |
| `graphviz` (binary) | Python `graphviz` package, ERD rendering | Both Dockerfiles |
| `curl` | Docker healthcheck probes | Both Dockerfiles |
| `libgl1` | OpenCV / moviepy (video frame reading) | `Dockerfile.streamlit` |
| `libglib2.0-0` | OpenCV / moviepy | `Dockerfile.streamlit` |
