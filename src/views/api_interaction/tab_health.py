import streamlit as st
import time
import requests

def render_health_tab(api_base_url):
    st.subheader("🏥 Live Health Dashboard")
    st.caption("Probe all major services simultaneously and see response times.")

    HEALTH_ENDPOINTS = [
        ("FastAPI Core",       "GET",  "/health"),
        ("Auth Service",       "POST", "/auth/token"),        # 422 = reachable
        ("Ingest Service",     "GET",  "/health"),             # reuse health
        ("Model Registry",     "GET",  "/models/list"),
        ("RAG / NLQ",          "POST", "/rag/nlq"),
        ("Agent Pipeline",     "POST", "/agents/query"),
        ("Admin Panel",        "GET",  "/admin/permissions"),
        ("Graph Store",        "GET",  "/admin/graph-data"),
    ]

    if st.button("🔄 Refresh All Health", type="primary", use_container_width=True):
        auth_hdrs = {}
        if st.session_state.get("auth_token"):
            auth_hdrs["Authorization"] = f"Bearer {st.session_state.auth_token}"
        results = {}
        _prog = st.progress(0)
        for i, (svc, method, ep) in enumerate(HEALTH_ENDPOINTS):
            try:
                t0 = time.time()
                if method == "GET":
                    r = requests.get(f"{api_base_url}{ep}", headers=auth_hdrs, timeout=5)
                else:
                    r = requests.post(f"{api_base_url}{ep}", headers=auth_hdrs, json={}, timeout=5)
                results[svc] = (r.status_code, time.time() - t0)
            except Exception:
                results[svc] = (0, 0.0)
            _prog.progress((i + 1) / len(HEALTH_ENDPOINTS))
        st.session_state["health_results"] = results

    if "health_results" in st.session_state:
        _hr = st.session_state["health_results"]
        cols = st.columns(4)
        for i, (svc, _, _ep_path) in enumerate(HEALTH_ENDPOINTS):
            sc, lat = _hr.get(svc, (0, 0.0))
            if sc in (200, 201):       icon, colour = "✅", "#2ecc71"
            elif sc in range(400,500): icon, colour = "⚠️", "#f39c12"
            elif sc == 0:              icon, colour = "🔴", "#e74c3c"
            else:                      icon, colour = "🟡", "#f1c40f"
            cols[i % 4].metric(
                label=f"{icon} {svc}",
                value=f"HTTP {sc}" if sc else "Unreachable",
                delta=f"{lat:.2f}s" if lat else None,
                delta_color="off"
            )

        st.divider()
        # Summary
        ok_count   = sum(1 for sc, _ in _hr.values() if 200 <= sc < 300)
        warn_count = sum(1 for sc, _ in _hr.values() if 400 <= sc < 500)
        err_count  = sum(1 for sc, _ in _hr.values() if sc == 0 or sc >= 500)
        total = len(_hr)
        s1, s2, s3 = st.columns(3)
        s1.metric("✅ Healthy", f"{ok_count}/{total}")
        s2.metric("⚠️ Auth/Input Issues", f"{warn_count}/{total}")
        s3.metric("❌ Unreachable", f"{err_count}/{total}")
    else:
        st.info("Click **Refresh All Health** above to probe all services.")

    st.divider()
    st.markdown("### 📖 Complete API Reference")
    with st.expander("All Endpoints — Quick Reference"):
        st.markdown("""
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/token` | — | Login → JWT |
| POST | `/auth/register` | — | Create user account |
| POST | `/auth/forgot-password` | — | Request password reset |
| POST | `/auth/reset-password` | — | Confirm reset via token |
| GET | `/keys/` | 🔐 | List API keys |
| POST | `/keys/generate` | 🔐 | Create API key |
| DELETE | `/keys/{id}` | 👑 | Revoke API key |
| POST | `/ingest/file` | 🔐 | Upload CSV/PDF/image/audio |
| POST | `/ingest/execute-sql` | 👑 | Run SQL script |
| POST | `/agents/query` | 🔐 | Multi-agent RAG pipeline |
| POST | `/rag/nlq` | 🔐 | Lightweight SQL NLQ |
| GET | `/models/list` | 🔐 | List ML models |
| GET | `/models/available` | 🔐 | Discover LLMs |
| POST | `/models/score` | 🔐 | Score via LLM/model |
| POST | `/ml/score` | 🔐 | Score via ML workflow model |
| POST | `/reports/generate` | 🔐 | Generate PDF report |
| GET | `/admin/users` | 👑 | List users |
| PATCH | `/admin/users/{id}` | 👑 | Update user role |
| PATCH | `/admin/users/{id}/email` | 👑 | Update email |
| PATCH | `/admin/users/{id}/username` | 👑 | Update username |
| PATCH | `/admin/users/{id}/password` | 👑 | Force password reset |
| DELETE | `/admin/users/{id}` | 👑 | Delete user |
| GET | `/admin/permissions` | 🔐 | Get my page permissions |
| GET | `/admin/roles` | 👑 | List all roles/permissions |
| POST | `/admin/roles` | 👑 | Create/update role |
| DELETE | `/admin/roles/{name}` | 👑 | Delete role |
| POST | `/admin/clean-db` | 👑 | Reset SQL database |
| POST | `/admin/delete-uploads` | 👑 | Delete all uploads |
| GET | `/admin/graph-data` | 🔐 | Get graph nodes/edges |
| GET | `/admin/graph-evaluation` | 🔐 | Graph health evaluation |
| POST | `/admin/rebuild-graph` | 👑 | Rebuild from uploads |
| POST | `/admin/project-data-to-graph` | 👑 | SQL → Graph projection |
| POST | `/admin/delete-graph` | 👑 | Delete all graph nodes |
| GET | `/health` | — | API health check |

🔐 = Bearer token required &nbsp;|&nbsp; 👑 = Admin role required
""")
