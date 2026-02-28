# 🔌 API Integration Hub — User Manual

**Page:** API Integration Hub (`pages/10_🔌_API_Interaction.py (wrapper for src/views/api_interaction/)`)  
**Access Level:** Authenticated Users (some endpoints require Admin role)

---

## Overview

The **API Integration Hub** is a live testing console for all Sentinel Pro FastAPI backend endpoints. It allows developers and admins to test API calls directly from the browser, inspect responses, copy cURL commands, and monitor a request history log.

---

## Sidebar Configuration

### Base URL
Set the FastAPI base URL. Default is `http://fastapi:8000` (Docker internal network).  
If testing from outside Docker, change to `http://localhost:8000`.

**Check Connectivity** — pings `GET /health` and shows the response.

### LLM Discovery
Probes `GET /models/available` to populate the LLM dropdown used in Intelligence tab forms. Click **🔄 Refresh** to force re-discovery.

### Request History
Shows the last 12 requests made in this session:
- Method (GET/POST/PATCH/DELETE)
- Endpoint path
- HTTP status code
- Response time in seconds

---

## Auth Requirements Legend

Throughout the Hub, endpoints are labelled:
- 🔐 **auth** — requires a Bearer token (login first)
- 👑 **admin** — requires admin role

---

## Tab 1 — 🔒 Identity & Auth

### POST `/auth/token` — Login
Enter **Username** and **Password** and click **🔐 Login** to get a JWT Bearer token.  
The token is stored in session state and automatically sent with all subsequent requests.

### POST `/auth/register` — Register
Create a new user account with:
- **Username** (required)
- **Email** (optional)
- **Password** (minimum 8 characters)
- **Role**: `guest`, `data_scientist`, or `admin`

### POST `/auth/forgot-password` — Request Password Reset
Enter an email address to trigger a password reset link.  
If SMTP is not configured, the reset token is logged to the console (mock mode).

### POST `/auth/reset-password` — Confirm Reset
Enter the **reset token** (from email or console log) and a **new password** to complete the reset.

### API Key Management

| Endpoint | Action |
|---|---|
| `GET /keys/` | List all active API keys |
| `POST /keys/generate` | Create a new named API key |
| `DELETE /keys/{id}` | Revoke a key by ID |

---

## Tab 2 — 📁 Ingestion

### POST `/ingest/file` — Upload File
Upload any supported file type (CSV, PDF, PNG, JPG, MP3, MP4, SQL). On success, the system returns the created table name, row count, or processing summary.

### POST `/ingest/execute-sql` — Execute SQL Script
Upload a `.sql` file to execute against SQLite. **Admin only.** Useful for seeding data without using the Data Hub UI.

---

## Tab 3 — 🧠 Intelligence

### POST `/agents/query` — Multi-Agent Pipeline
The full RAG pipeline with sample question presets:

| Parameter | Description |
|---|---|
| `question` | Natural language question |
| `llm_id` | e.g. `openai:gpt-4o-mini` |
| `k_candidates` | Number of retrieved context chunks |
| `bypass_agents` | `true` = fast mode (skip deep analysis) |
| `rebuild_kb` | `true` = force Knowledge Base rebuild |

### POST `/rag/nlq` — Legacy SQL NLQ
Lightweight SQL natural-language query without the full agent pipeline. Faster for simple lookups.

---

## Tab 4 — 🤖 ML Models

### Model Registry
- `GET /models/list` — show all registered ML model versions
- `GET /models/available` — show all discovered LLMs (Ollama + cloud)

### ML Scoring
- `POST /models/score` — score via any registered LLM/model
- `POST /ml/score` — score via a trained ML Workflow model (XGBoost/RandomForest)

### Report Generation
- `POST /reports/generate` — generate a PDF fraud report with `analysis_type` = `full | summary | fraud`

---

## Tab 5 — 📊 Admin & Infra

### 👥 User Management
Full CRUD operations for user accounts:

| Endpoint | Action |
|---|---|
| `GET /admin/users` | List all users |
| `PATCH /admin/users/{id}` | Update role |
| `PATCH /admin/users/{id}/email` | Update email |
| `PATCH /admin/users/{id}/username` | Update username |
| `PATCH /admin/users/{id}/password` | Force password reset |
| `DELETE /admin/users/{id}` | Delete account |

### 🎭 Role & Permissions
| Endpoint | Action |
|---|---|
| `GET /admin/permissions` | Get current user's page permissions |
| `GET /admin/roles` | List all roles with their page access |
| `POST /admin/roles` | Create or update a role |
| `DELETE /admin/roles/{name}` | Delete a role |

### 🗄️ Storage & Graph
| Endpoint | Action |
|---|---|
| `POST /admin/clean-db` | ⚠️ Reset SQLite database |
| `POST /admin/delete-uploads` | ⚠️ Delete all uploaded files |
| `GET /admin/graph-data` | Fetch all graph nodes and relationships |
| `GET /admin/graph-evaluation` | Run graph health evaluation |
| `POST /admin/rebuild-graph` | Rebuild graph from uploads |
| `POST /admin/project-data-to-graph` | Project SQL tables as graph nodes |
| `POST /admin/delete-graph` | ⚠️ Delete all graph nodes |

---

## Tab 6 — 🏥 Health Dashboard

Click **🔄 Refresh All Health** to probe 8 services simultaneously:
- FastAPI Core, Auth Service, Model Registry, RAG/NLQ, Agent Pipeline, Admin Panel, Graph Store

Results show HTTP status code and response time. A summary row displays counts for healthy / warning / unreachable services.

**Complete API Reference table** at the bottom lists all 33 endpoints with method, path, and auth requirements.

---

## cURL Command Export

Every successful API call shows a collapsible **📋 cURL Command** block with the full command ready to copy and run from a terminal. This is useful for integrating with external systems.

---

## Tips

- Login first (`POST /auth/token`) — the token auto-populates for all subsequent requests.
- Use **⚡ Speed Mode** in the Agent Pipeline form to avoid timeouts with slow LLMs.
- The **⚠️ Admin Only** endpoints will return HTTP 403 if you are not logged in as admin.
- The request history persists for the session — useful for debugging a sequence of API calls.
