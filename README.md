# 🧠 Fraud Investigation Workbench Pro

[![CI Pipeline](https://github.com/your-org/Fraud-AI-Workbench-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/Fraud-AI-Workbench-pro/actions/workflows/ci.yml)

*A full multi-agent, RAG-powered, ML-enabled fraud detection platform — Streamlit frontend + FastAPI backend + Neo4j graph store.*

---

## 🚀 Overview

The **Fraud Investigation Workbench Pro** is a complete, end-to-end fraud analysis platform designed for:

- Fraud detection model development
- SQL RAG + agentic analysis (multi-agent SQL reasoning)
- Trend visualization & anomaly detection
- Fraud risk scoring & PDF reporting
- Graph-based entity analysis (Neo4j)
- Multi-page Streamlit UI + Production FastAPI backend

---

## 🏗️ Architecture

```
              ┌──────────────────────────────┐
              │         Streamlit UI          │
              │  Multi-page · CSV Upload      │
              │  SQL RAG · EDA · ML Scoring   │
              └──────────────┬───────────────┘
                             │ REST calls
                             ▼
              ┌──────────────────────────────┐
              │        FastAPI Backend        │
              │  SQL RAG · ML Scoring         │
              │  Ingestion · Admin · Auth     │
              │  Reports · Graph API          │
              └──┬──────────┬───────────┬────┘
                 ▼          ▼           ▼
          SQLite DB    FAISS Vector   Neo4j Graph
          (raw data)   (knowledge)    (entities)
                                  ML Models (sklearn)
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| Multi-Agent SQL RAG | LLM SQL generation, JOIN recovery, fallback agents, reconciliation |
| Dynamic CSV Ingestion | Auto SQLite tables, schema detection, ERD generation, KB rebuild |
| Trends & Insights | Altair charts, LLM-generated EDA narrative |
| Anomaly Detection | IQR-based detection, fraud risk scoring, LLM narrative |
| ML Pipeline | Auto-training (Logistic Regression, Random Forest), real-time scoring |
| PDF Reporting | Full SQL/RAG analysis PDF export |
| Admin Panel | User management, role-based permissions, API keys |
| Authentication | JWT-based auth, role enforcement |

---

## 📂 Project Structure

```
Fraud-AI-Workbench-pro/
├── .github/                   # GitHub Actions CI/CD workflows
├── src/                       # All Python source code
│   ├── app.py                 # Streamlit entrypoint
│   ├── api/                   # FastAPI backend (routers, models)
│   ├── pages/                 # Streamlit multipage UI wrappers
│   ├── views/                 # Refactored page sub-modules (tabs, rendering)
│   ├── agents/                # Multi-agent system + LangGraph
│   ├── ml/                    # ML pipeline (data_prep, train, score)
│   ├── rag_sql/               # SQL RAG engine, schema, ERD logic
│   ├── components/            # Sidebar, charts, shared UI components
│   ├── config/                # Settings (Pydantic BaseSettings)
│   ├── scripts/               # Data init, compression, doc generators
│   └── utils/                 # Auth utils, version manager, email
├── tests/                     # Unit, integration, e2e test suite
├── data/                      # Runtime data (DB, uploads, vector store)
├── models/                    # Trained ML model files
├── Dockerfile.fastapi
├── Dockerfile.streamlit
├── docker-compose.yml
├── docker-compose.neo4j.yml
├── setup_infra.sh             # Mac/Linux: start Neo4j + network
├── setup_infra.bat            # Windows: start Neo4j + network
└── requirements.txt
```

---

## 🔧 Prerequisites

- **Docker Desktop** (Mac, Linux, or Windows) — required for all deployment modes
- **Python 3.11+** — for local development only
- **At least one LLM API key** — OpenAI, DeepSeek, Google, or Anthropic

---

## ⚙️ 1. Configure Environment Variables

> [!IMPORTANT]
> **Do this before running any Docker command.** Missing `SECRET_KEY` or `GRAPH_STORE_PASSWORD` will cause the app to start with insecure defaults.

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Required variables:

```env
# LLM (at least one required)
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...

# Security — MUST be changed (generate with: openssl rand -hex 32)
SECRET_KEY=<your-strong-random-secret>

# Neo4j Graph Store
GRAPH_STORE_URI=bolt://localhost:7687
GRAPH_STORE_USER=neo4j
GRAPH_STORE_PASSWORD=<your-neo4j-password>
```

> [!WARNING]
> Never commit your `.env` file to version control. It is already listed in `.gitignore`.

---

## 🐳 2. Create the Docker Network (Once)

The two compose files share a custom Docker network. Create it once:

```bash
# Mac / Linux
docker network create fraud_network

# Windows (PowerShell or CMD)
docker network create fraud_network
```

---

## 🗄️ 3. Start Neo4j Graph Store

Neo4j must be running **before** the main app stack — the FastAPI startup probe will wait for it.

### Mac / Linux
```bash
chmod +x setup_infra.sh
./setup_infra.sh
```

### Windows (double-click or run in CMD)
```bat
setup_infra.bat
```

> [!IMPORTANT]
> **CRITICAL STARTUP REQUIREMENT:** Neo4j (loaded with APOC + Graph Data Science plugins) is extremely heavy. It takes **~60 seconds** to fully initialize on its first run. 
> 
> **DO NOT proceed to Step 4 until Neo4j is completely online.** If you start the main application while Neo4j is still booting, the FastAPI backend will fail to connect.
> 
> Watch the logs to confirm it is ready:
> `docker logs -f fraud_neo4j`

---

## 🚀 4. Start the Application

```bash
# Mac / Linux / Windows (Docker Desktop required)
docker compose up --build
```

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8504 |
| FastAPI backend | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

> [!TIP]
> On first startup, `streamlit` waits for `fastapi` to pass its health check before starting.
> This prevents "backend not ready" errors during boot.

---

## 🛑 Key Security Requirements

> [!CAUTION]
> The following steps are **mandatory** before exposing this application to a network.

### ① Change the JWT Secret Key
The default `SECRET_KEY` in `config/settings.py` is insecure. Override it via `.env`:
```env
SECRET_KEY=<output of: openssl rand -hex 32>
```

### ② Set a Strong Neo4j Password
The compose files read `GRAPH_STORE_PASSWORD` from your environment. Never leave it as `password`:
```env
GRAPH_STORE_PASSWORD=<strong-random-password>
```

### ③ Restrict CORS Origins
By default `ALLOWED_ORIGINS` allows `localhost`. For production, set:
```env
ALLOWED_ORIGINS=https://your-domain.com
```

### ④ Do Not Expose `.env` or Admin Endpoints
Ensure `.env` is in `.gitignore` (it is by default). Admin endpoints at `/admin/*` require an `admin` role JWT — protect port 8000 behind a reverse proxy in production.

---

## 🧪 Testing & CI/CD

The project includes a robust suite of Unit, Integration, and End-to-End tests located in `tests/`.

### Local Testing
```bash
# Install test dependencies
pip install pytest flake8 pytest-cov

# Run all unit tests
PYTHONPATH=src pytest tests/unit/ -v

# Run integration tests (requires docker-compose up -d)
PYTHONPATH=src pytest tests/integration/ -v
```

### GitHub Actions (Continuous Integration)
This project is fully CI/CD enabled! Upon each `push` or `pull_request` to the `main` branch, GitHub Actions will automatically:
1. Lint the codebase using `flake8`.
2. Run the full `tests/unit/` suite.
3. Spin up the Database and FastAPI backend dynamically in Docker.
4. Run the `tests/integration/` and `tests/e2e/` suites against the live API.

For detailed guidelines on writing tests and contributing features, please read our [CONTRIBUTING.md](documentation/references/CONTRIBUTING.md) guide.

---

## ▶️ Local Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Start Streamlit (separate terminal)
streamlit run app.py
```

---

## 🧩 Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'api'` | Run `pytest` from the project root; `pytest.ini` adds `.` to `sys.path` |
| Neo4j shows `unhealthy` | The old healthcheck used `curl` (not in the neo4j image). Pull latest config and restart: `./setup_infra.sh` |
| Streamlit can't reach backend | Check `API_URL=http://fastapi:8000` in docker-compose; FastAPI container must be healthy |
| SQL error on first run | Upload a CSV first via the **Data Hub** page to create the SQLite tables |
| ML scoring fails | Ensure a model has been trained via the **ML Workflow** page |
| No ERD generated | Upload at least two related tables with matching column names |
| `SECRET_KEY` warning in logs | Set `SECRET_KEY` in your `.env` file (see Security section above) |

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
