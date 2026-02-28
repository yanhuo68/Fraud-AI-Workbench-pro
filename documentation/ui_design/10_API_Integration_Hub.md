# 🔌 API Integration Hub — UI Design Specification

**Page:** `pages/10_🔌_API_Interaction.py (wrapper for src/views/api_interaction/)`  
**Layout:** Wide  
**Theme:** Dark Glassmorphism

---

## Page Layout Overview

```
┌──────────────────────────┬────────────────────────────────────────┐
│  SIDEBAR (API config)    │  🔌 API Integration Hub  [st.title]   │
│  ─────────────────────── │  "Live testing console..." [caption]  │
│  Base URL: [text input]  ├────────────────────────────────────────┤
│  [🔗 Check Connectivity] │  [🔒 Identity] [📁 Ingest] [🧠 Intel] │
│  ─────────────────────── │  [🤖 ML] [📊 Admin] [🏥 Health]       │  ← 6 tabs
│  🤖 LLM Discovery        ├────────────────────────────────────────┤
│  Status: Found 7         │  [Tab form content area]              │
│  [🔄 Refresh LLMs]       │                                        │
│  ─────────────────────── │  ── Response Panel ──                  │
│  📜 Request History      │  [Status badge] [latency] [method+URL]│
│  🟢 POST /auth/token     │  [📋 cURL command expander]           │
│     HTTP 200 · 0.23s     │  [JSON / binary response body]        │
│  🔴 GET /models/list     │                                        │
│     HTTP 401 · 0.11s     │                                        │
│  [🗑 Clear History]       │                                        │
└──────────────────────────┴────────────────────────────────────────┘
```

---

## Sidebar (API Hub-Specific)

### Base URL Input
```
┌──────────────────────────────────────┐
│  Base URL                            │
│  [http://fastapi:8000              ] │
│  [🔗 Check Connectivity]             │
└──────────────────────────────────────┘
```
- `st.text_input("Base URL", value="http://fastapi:8000")`
- Connectivity button pings `GET /health` and shows `st.success()` / `st.error()`

### Request History Panel
- Last 12 requests shown in reverse order
- Per entry: `st.caption("🟢 POST /auth/token\nHTTP 200 · 0.23s")`
- `🟢` for 2xx, `🔴` for errors/4xx/5xx
- `st.button("🗑 Clear History")` at top

---

## Endpoint Badge Component

Inline HTML method badge before each endpoint:

```
[POST] /auth/token  🔐 auth
[GET]  /admin/users  👑 admin
```

```css
/* POST */   background: #49cc90; color: white; padding: 3px 10px; border-radius: 5px; font-family: monospace;
/* GET */    background: #61affe;
/* PATCH */  background: #50e3c2; color: #333;
/* DELETE */ background: #f93e3e; color: white;
/* path */   font-family: monospace; color: #e0e0e0;
/* 🔐 */     color: #f39c12; font-size: 0.78rem;
/* 👑 */     color: #e74c3c; font-size: 0.78rem;
```

---

## Tab 1 — 🔒 Identity & Auth

Two-column layout `st.columns(2)`:

**Left column:**
```
POST /auth/token
[Login form: Username, Password, Submit]

POST /auth/register
[Register form: Username, Email, Password, Role ▾, Submit]

POST /auth/forgot-password
[Email input, Submit]

POST /auth/reset-password
[Token input, New Password, Submit]
```

**Right column:**
```
GET /keys/
[List Keys button]

POST /keys/generate
[Key Name input, Generate button]

DELETE /keys/{id}
[Key ID number input, Revoke button]
```

Each endpoint group:
- Method badge + path header
- `st.caption()` explanation
- `st.form()` with submit button

---

## Tab 2 — 📁 Ingestion

Two-column layout:

```
Left:                               Right:
POST /ingest/file                   POST /ingest/execute-sql
[Supported types expander]          [How it works expander]
[st.file_uploader]                  [SQL file uploader]
[⬆️ Ingest File button]             [▶️ Execute SQL Script button]
```

---

## Tab 3 — 🧠 Intelligence

Inner tabs: `[🤖 Multi-Agent Pipeline] [🔍 Legacy SQL NLQ]`

### Multi-Agent Pipeline
```
Quick Sample: [dropdown ▾]
Request Schema: [st.expander]

[Question text area]
[LLM ▾]  [k slider 1-5]
[⚡ Speed Mode checkbox]  [🔄 Rebuild KB checkbox]
[🚀 Run Agent Pipeline — primary full-width]
```

### Legacy SQL NLQ
```
Quick Sample: [dropdown ▾]
Request Schema: [st.expander]

[Question text input]
[LLM ▾]
[🔍 Run NLQ — full-width]
```

---

## Tab 4 — 🤖 ML Models

Inner tabs: `[📋 Model Registry] [🎯 ML Scoring] [📝 Report Generation]`

**Registry:** Two buttons side-by-side (List Models / Discover LLMs)  
**Scoring:** Two-column layout (models/score left, ml/score right)  
**Reports:** Single form with analysis_type dropdown and data_context JSON textarea

---

## Tab 5 — 📊 Admin & Infra

Three inner tabs: `[👥 User Management] [🎭 Role & Permissions] [🗄️ Storage & Graph]`

**User Management:** Two columns — list/delete left, PATCH forms (role/email/username/password) stacked right  
**Roles:** Two columns — list/permissions left, create/delete right  
**Storage:** Two columns — DB operations (clean-db, delete-uploads) left, graph operations right

---

## Tab 6 — 🏥 Health Dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│  [🔄 Refresh All Health — primary, full-width]                   │
│  [████████████████████████] Progress bar (while probing)        │
├────────────┬────────────┬────────────┬────────────────────────────┤
│ ✅ FastAPI  │ ⚠️ Auth     │ ✅ ML Reg   │ ✅ RAG/NLQ               │
│ HTTP 200   │ HTTP 422   │ HTTP 200   │ HTTP 200                  │
│ 0.12s      │ 0.08s      │ 0.19s      │ 0.34s                     │
├────────────┴────────────┴────────────┴────────────────────────────┤
│  ✅ Healthy: 6/8   ⚠️ Auth/Input: 1/8   ❌ Unreachable: 1/8      │  ← 3-col summary
└──────────────────────────────────────────────────────────────────┘
```

- Service tiles: `st.metric(label, value, delta)` in `st.columns(4)`
- Summary row: `st.columns(3)` with `st.metric()`
- Reference table: `st.expander("All Endpoints — Quick Reference")` → markdown table

---

## Response Panel (Common to All Tabs)

After any request:

```
┌────────────────────────────────────────────────────────────┐
│  ✅ 200  │  0.24s  │  POST http://fastapi:8000/auth/token  │
├────────────────────────────────────────────────────────────┤
│  📋 cURL Command  [▾]                                      │
│  curl -X POST 'http://fastapi:8000/auth/token' \          │
│    --data-urlencode 'username=yanhuo68' \                  │
│    --data-urlencode 'password=...'                         │
├────────────────────────────────────────────────────────────┤
│  {                                                         │
│    "access_token": "eyJhb...",                            │
│    "token_type": "bearer"                                  │
│  }                                                         │
└────────────────────────────────────────────────────────────┘
```

| Element | Spec |
|---|---|
| Status badge | Inline HTML `<span>` green/amber/red pill |
| Latency | `st.markdown("⏱ **0.24s**")` |
| URL | `st.markdown(f"\`{method} {url}\`")` |
| cURL | `st.expander("📋 cURL Command")` → `st.code(..., language="bash")` |
| JSON | `st.json(response.json())` |
| Binary | `st.download_button("⬇ Download", content)` |

---

## Colour Summary

| Element | Colour |
|---|---|
| POST badge | `#49cc90` green |
| GET badge | `#61affe` blue |
| PATCH badge | `#50e3c2` teal |
| DELETE badge | `#f93e3e` red |
| 2xx status pill | `#2ecc71` |
| 4xx status pill | `#f39c12` |
| 5xx/0 status pill | `#e74c3c` |
| 🔐 auth label | `#f39c12` |
| 👑 admin label | `#e74c3c` |
