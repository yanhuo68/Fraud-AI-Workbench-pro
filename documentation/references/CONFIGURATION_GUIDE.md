# ⚙️ System Configuration Guide

**Project:** Sentinel Fraud Investigation Workbench Pro  
**Configuration entry point:** `config/settings.py` → `Settings` class (Pydantic BaseSettings)  
**Loading order:** `.env` file → Environment variables (docker-compose `environment:`) → Coded defaults

---

## How Configuration Works

```
┌─────────────────────────────────────────────────────────┐
│                   Configuration Flow                     │
│                                                         │
│  .env file                                              │
│  (project root)  ──┐                                    │
│                    ▼                                    │
│  Docker-compose    │   pydantic-settings                │
│  environment: ──► Settings() ──► settings instance      │
│                    │             (singleton)             │
│  System ENV    ────┘                                    │
│  variables                                              │
│                                                         │
│  Priority: ENV vars > .env file > coded defaults        │
└─────────────────────────────────────────────────────────┘
```

The `Settings` class (`config/settings.py`) is a **Pydantic `BaseSettings`** model:
- Reads from the `.env` file in the project root
- Overridden by any matching environment variable (case-insensitive)
- All field names support both lowercase and UPPER_CASE aliases
- Validated and type-coerced at startup — the app fails fast if a required value is missing or invalid

The singleton is instantiated once at module load:
```python
settings = Settings()
```

All application modules import `settings` from `config.settings` — no direct `os.getenv()` calls should bypass this.

---

## Complete Settings Reference

### 🔑 LLM API Keys

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `openai_api_key` | `OPENAI_API_KEY` | `""` | str | Passed to `openai.OpenAI(api_key=...)` via `llm_router`; empty = OpenAI unavailable |
| `deepseek_api_key` | `DEEPSEEK_API_KEY` | `""` | str | Passed to DeepSeek HTTP client; empty = DeepSeek unavailable |
| `google_api_key` | `GOOGLE_API_KEY` | `""` | str | Passed to `langchain-google-genai`; required for Gemini models |
| `anthropic_api_key` | `ANTHROPIC_API_KEY` | `""` | str | Passed to `anthropic.Anthropic(api_key=...)` for Claude models |

**Setting API keys:**
```bash
# In .env file (project root):
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
```

**Effect:** The `llm_router.get_available_llms()` function checks which keys are present and non-empty, returning only providers that have valid credentials. The sidebar LLM dropdown population is driven by this check.

---

### 🗄️ Database Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `db_path` | `DB_PATH` | `data/db/rag.db` | str | SQLAlchemy `create_engine(f"sqlite:///{db_path}")` → stores users, roles, uploaded file metadata |

**Docker override:** `DB_PATH=/app/data/db/rag.db` (absolute path inside container)

**Parent directory creation:** Pydantic validator `ensure_parent_dirs` creates `data/db/` at startup if it doesn't exist.

**Effect on system:**
- `api/database.py` uses this to create the SQLite engine
- SQLite is a file-based database — the file is on the Docker volume (`.:/app`) so data persists across container restarts
- If the path is wrong, the FastAPI backend will fail to start

---

### 🌐 API Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `api_url` | `API_URL` | `http://localhost:8000` | str | Used by Streamlit pages for all `requests.post/get()` calls to the backend |
| `api_host` | `API_HOST` | `0.0.0.0` | str | Uvicorn bind address |
| `api_port` | `API_PORT` | `8000` | int | Uvicorn listen port |

**Docker override:** `API_URL=http://fastapi:8000` — uses Docker's internal DNS name `fastapi` to reach the API container from the Streamlit container.

**Effect on system:**
- All Streamlit pages call the API via `settings.api_url`
- If `API_URL` points to `localhost:8000` in Docker, requests will fail because `localhost` inside the Streamlit container refers to that container, not the FastAPI container
- The `http://fastapi:8000` value resolves via Docker's `fraud_network` bridge network

---

### 📁 File Upload Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `max_file_size_mb` | `MAX_FILE_SIZE_MB` | `100` | int | FastAPI validates `Content-Length` before processing upload (`/ingest/file`) |
| `allowed_extensions` | `ALLOWED_EXTENSIONS` | csv,pdf,txt,json,md,png,jpg,jpeg,webp,mp3,wav,m4a,mp4,mov,avi | str (comma-sep) | File type whitelist checked in `api/routers/ingest.py` |
| `uploads_dir` | `UPLOADS_DIR` | `Data/uploads` | str | Uploaded files saved here; file picker in Multimodal RAG reads from here |

**Helper methods:**
```python
settings.get_allowed_extensions_list()  # → ["csv", "pdf", "png", ...]
settings.get_max_file_size_bytes()      # → 104857600 (100 MB)
```

**Effect on system:**
- Files larger than `max_file_size_mb` are rejected with HTTP 413
- Files with extensions not in `allowed_extensions` are rejected with HTTP 422
- All uploaded files land in `uploads_dir` — this directory is on the shared Docker volume

---

### 🔒 CORS Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `allowed_origins` | `ALLOWED_ORIGINS` | `http://localhost:8504,http://localhost:3000` | str | FastAPI `CORSMiddleware` origin whitelist |

**Helper method:**
```python
settings.get_allowed_origins_list()  # → ["http://localhost:8504", ...]
```

**Usage in `api/main.py`:**
```python
app.add_middleware(CORSMiddleware, allow_origins=settings.get_allowed_origins_list(), ...)
```

**Effect:** In Docker, CORS is typically not an issue since both containers are on the same network. In standalone dev mode, add `http://localhost:8504` (Streamlit) to allow the browser to call the API directly from the JavaScript layer.

---

### 📝 Logging Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `log_level` | `LOG_LEVEL` | `INFO` | str | Validated to `DEBUG/INFO/WARNING/ERROR/CRITICAL`; applied to Python `logging` root logger |
| `log_file` | `LOG_FILE` | `logs/run.log` | str | Log file path; parent dir `logs/` created at startup |

**Effect on system:**
- Set `LOG_LEVEL=DEBUG` to see all SQL queries, LLM prompts, and API request traces
- Log file persists on the Docker volume — accessible at `logs/run.log` on the host

---

### 🤖 Model Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `model_dir` | `MODEL_DIR` | `models/` | str | Trained ML models saved/loaded via `joblib.dump/load()` at `{model_dir}/{name}.pkl` |

**Docker override:** `MODEL_DIR=/app/models`

**Effect:** ML Workflow tab lists models found in this directory. Deployed scoring API (`/models/score`) loads from here.

---

### 📚 Knowledge Base Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `kb_dir` | `KB_DIR` | `data/kb` | str | FAISS index files and metadata stored here; one subfolder per indexed source |
| `docs_dir` | `DOCS_DIR` | `docs` | str | Raw documentation files indexed for the App Guide Agent |

**Effect on system:**
- RAG pipelines check for existing FAISS indexes in `kb_dir` before rebuilding
- Rebuilding the KB (via API or sidebar button) re-reads files from `uploads_dir` and `docs_dir`, re-embeds, and overwrites the index in `kb_dir`
- First startup: no KB exists → first RAG query triggers auto-build

---

### 🕸️ Graph Store (Neo4j) Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `graph_store_uri` | `GRAPH_STORE_URI` | `bolt://localhost:7687` | str | Neo4j Bolt protocol URI |
| `graph_store_user` | `GRAPH_STORE_USER` | `neo4j` | str | Neo4j username |
| `graph_store_password` | `GRAPH_STORE_PASSWORD` | `""` | str | Neo4j password |

**Docker override (both containers):**
```
GRAPH_STORE_URI=bolt://fraud_neo4j:7687
GRAPH_STORE_USER=neo4j
GRAPH_STORE_PASSWORD=password
```

**Property access:**
```python
driver = settings.graph_driver  # Returns neo4j.GraphDatabase.driver(...)
```

**Effect on system:**
- Graph RAG agent uses the driver to run Cypher queries
- If Neo4j is not running, the Graph RAG page shows connection error
- The password must match `NEO4J_AUTH=neo4j/password` in `docker-compose.neo4j.yml`
- Neo4j must be on the same `fraud_network` Docker bridge network

---

### 📧 SMTP Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `smtp_server` | `SMTP_SERVER` | `""` | str | SMTP host; empty = Mock mode (log to console) |
| `smtp_port` | `SMTP_PORT` | `587` | int | SMTP port (587 STARTTLS, 465 SSL, 25 plaintext) |
| `smtp_username` | `SMTP_USERNAME` | `""` | str | SMTP auth username |
| `smtp_password` | `SMTP_PASSWORD` | `""` | str | SMTP auth password |
| `smtp_sender_email` | `SMTP_SENDER_EMAIL` | `""` | str | `From:` email address |

**Mock mode:** If `SMTP_SERVER` is empty, `utils/email_utils.py` logs the email content to stdout instead of sending — useful for development and demo environments.

**Real SMTP example (.env):**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SENDER_EMAIL=your_email@gmail.com
```

**Effect on system:**
- Forgot-password flow sends a reset link to the user's email
- In mock mode: check FastAPI container stdout (`docker compose logs fastapi`) for the reset token
- Admin Console → SMTP Configuration tab lets admins update these values at runtime

---

### ⏱️ SQL Query Limits

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `sql_timeout_seconds` | `SQL_TIMEOUT_SECONDS` | `30` | int | Max seconds a SQL query may run before cancellation |
| `sql_max_rows` | `SQL_MAX_ROWS` | `10000` | int | Max rows returned from any SQL query |

**Effect:** Prevents runaway queries from exhausting memory or blocking the event loop. Enforced at the SQL agent layer before results reach the UI.

---

### 🔐 Security Configuration

| Setting | Env Var | Default | Type | How It Works |
|---|---|---|---|---|
| `secret_key` | `SECRET_KEY` | `SUPER_SECRET_KEY_REPLACE_ME` | str | HMAC signing key for JWT tokens |
| `algorithm` | `ALGORITHM` | `HS256` | str | JWT signing algorithm |
| `access_token_expire_minutes` | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | int | JWT validity: 1440 min = 24 hours |

**⚠️ CRITICAL:** The default `SECRET_KEY` must be changed before any production deployment. Tokens signed with the default key can be forged if an attacker knows it.

**Generate a secure key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Effect on system:**
- `api/routers/auth.py` signs JWT with `SECRET_KEY` + `ALGORITHM`
- `utils/auth_utils.py:decode_access_token()` verifies incoming JWT
- `Depends(get_current_user)` on protected routes calls `decode_access_token` — if the token is expired or invalid, HTTP 401 is returned
- Default 24-hour expiry means users stay logged in across browser refreshes without a new login

---

## Environment Variable Quick-Reference

Copy this template to `.env` in the project root:

```bash
# ── LLM API Keys ───────────────────────────────────────────
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...

# ── Database ────────────────────────────────────────────────
DB_PATH=data/db/rag.db             # relative path from project root

# ── API ─────────────────────────────────────────────────────
API_URL=http://localhost:8000      # use http://fastapi:8000 in Docker
API_HOST=0.0.0.0
API_PORT=8000

# ── Files ───────────────────────────────────────────────────
MAX_FILE_SIZE_MB=100
UPLOADS_DIR=Data/uploads

# ── Knowledge Base & Models ────────────────────────────────
KB_DIR=data/kb
MODEL_DIR=models

# ── Neo4j Graph ────────────────────────────────────────────
GRAPH_STORE_URI=bolt://localhost:7687   # bolt://fraud_neo4j:7687 in Docker
GRAPH_STORE_USER=neo4j
GRAPH_STORE_PASSWORD=password

# ── SMTP (leave blank for Mock mode) ───────────────────────
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SENDER_EMAIL=

# ── Security ────────────────────────────────────────────────
SECRET_KEY=SUPER_SECRET_KEY_REPLACE_ME   # CHANGE THIS!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ── Logging ─────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FILE=logs/run.log

# ── SQL Limits ──────────────────────────────────────────────
SQL_TIMEOUT_SECONDS=30
SQL_MAX_ROWS=10000
```

---

## Docker Service Configuration

### Service: `fastapi` (`docker-compose.yml`)

| Property | Value | Effect |
|---|---|---|
| Container name | `fraud_api` | Referenced as `fastapi` on the Docker network |
| Build | `Dockerfile.fastapi` | Python 3.11-slim + BLAS/LAPACK/graphviz |
| Port | `8000:8000` | Host port 8000 → container port 8000 |
| Volume | `.:/app` | Live code mount (changes reflect without rebuild) |
| Network | `fraud_network` (external) | Shared with streamlit and neo4j containers |
| extra_hosts | `host.docker.internal:host-gateway` | Allows calling Ollama on the host machine from inside the container |

### Service: `streamlit` (`docker-compose.yml`)

| Property | Value | Effect |
|---|---|---|
| Container name | `fraud_streamlit` | Accessible on network as `streamlit` |
| Build | `Dockerfile.streamlit` | Python 3.11-slim + libgl1 for video |
| Port | `8504:8504` | Browser URL: `http://localhost:8504` |
| depends_on | `fastapi` | Docker waits for FastAPI container to start first |
| Healthcheck | `curl -f http://localhost:8504/` | Marks container healthy only after Streamlit responds |
| CORS disabled | `STREAMLIT_SERVER_ENABLECORS=false` | Prevents CORS issues when API calls are proxied server-side |

### Service: `graphdb` (`docker-compose.neo4j.yml`)

| Property | Value | Effect |
|---|---|---|
| Image | `neo4j:5.11.0` | Fixed version — GDS plugin version must match |
| Container name | `fraud_neo4j` | DNS name referenced by other services |
| Ports | `7474:7474`, `7687:7687` | 7474 = HTTP browser UI, 7687 = Bolt protocol |
| Volume: data | `./data/neo4j/data:/data` | Graph data persists across restarts |
| Volume: logs | `./data/neo4j/logs:/logs` | Neo4j server logs accessible from host |
| Volume: import | `./data/neo4j/import:/var/lib/neo4j/import` | CSV files here can be bulk-loaded via `LOAD CSV` |
| Auth | `NEO4J_AUTH=neo4j/password` | Sets initial username/password |
| Plugins | `["apoc", "graph-data-science"]` | APOC procedures + GDS algorithms (PageRank, Louvain) enabled |
| Procedures | `apoc.*,gds.*` unrestricted | Required for GDS algorithms to run |
| Memory | Heap max 1G, pagecache 512M | Tuned for moderate graph sizes (~1M nodes) |
| Healthcheck | 60s start period, 15 retries | Neo4j takes 30–60s to fully initialise on first start |

---

## App-level Persistent Configuration (`data/config/app_settings.json`)

Separate from the `Settings` class, this JSON file stores UI/operational state:

```json
{
  "quick_demo_installed": false
}
```

| Key | Values | Effect |
|---|---|---|
| `quick_demo_installed` | `true` / `false` | Controls whether the green "⚡ Quick Install" button appears; set to `true` after demo runs, reset to `false` to re-enable install |

**Managed by:** `utils/demo_installer.py` — `is_demo_already_installed()` and `_mark_installed()`  
**Admin reset:** Admin Console → Onboarding Settings → Reset Install Status

---

## Configuration Validation Rules

Validated at startup by `config/settings.py`:

| Field | Validator | Rule |
|---|---|---|
| `log_level` | `validate_log_level` | Must be one of `DEBUG/INFO/WARNING/ERROR/CRITICAL` |
| `db_path`, `log_file`, `model_dir`, `kb_dir`, `docs_dir` | `ensure_parent_dirs` | Parent directories are created automatically if missing |

**Startup failure modes:**
- Invalid `LOG_LEVEL` → `ValueError` raised, app exits
- Missing `SECRET_KEY` → Uses default (warning only, no crash) — change it before production
- Missing API keys → LLM provider excluded from dropdown, no crash

---

## Standalone (Non-Docker) Configuration

Run without Docker:

```bash
# 1. Create .env with at minimum:
API_URL=http://localhost:8000

# 2. Start FastAPI
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 3. Start Streamlit (separate terminal)
streamlit run app.py --server.port=8504

# 4. Optional: start Neo4j separately
docker run -d -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11.0
```

Standalone mode uses `API_URL=http://localhost:8000` (default) — this works because both processes are on the same machine.
