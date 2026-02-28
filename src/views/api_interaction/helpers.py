import streamlit as st
import requests
import json
import time

def get_available_llms(api_base_url):
    """Discover LLMs from backend or return defaults."""
    if "available_llms" not in st.session_state:
        auth_token = st.session_state.get("auth_token")
        if auth_token:
            try:
                st.session_state.discovery_status = "In Progress"
                r = requests.get(
                    f"{api_base_url}/models/available",
                    headers={"Authorization": f"Bearer {auth_token}"},
                    timeout=15
                )
                if r.status_code == 200:
                    models = r.json().get("llms", [])
                    st.session_state.available_llms = models
                    st.session_state.discovery_status = f"Found {len(models)}"
                    return models
            except Exception as e:
                st.session_state.discovery_status = f"Failed: {e}"
        st.session_state.discovery_status = "Using defaults"
    defaults = ["openai:gpt-4o-mini", "openai:gpt-4o", "anthropic:claude-3-5-sonnet-20241022",
                "google:gemini-1.5-pro", "deepseek:deepseek-chat",
                "local_ollama:llama3", "local_ollama:mistral"]
    return st.session_state.get("available_llms", defaults)

def _build_curl(method, url, hdrs, payload=None, is_form=False):
    parts = [f"curl -X {method} '{url}'"]
    for k, v in hdrs.items():
        parts.append(f"  -H '{k}: {v}'")
    if payload and not is_form:
        parts.append("  -H 'Content-Type: application/json'")
        parts.append(f"  -d '{json.dumps(payload)}'")
    elif payload and is_form:
        for k, v in payload.items():
            parts.append(f"  --data-urlencode '{k}={v}'")
    return " \\\n".join(parts)

def make_request(method, endpoint, api_base_url, payload=None, files=None, params=None):
    if "api_history" not in st.session_state:
        st.session_state.api_history = []
        
    url = f"{api_base_url}{endpoint}"
    hdrs = {}
    if st.session_state.get("auth_token"):
        hdrs["Authorization"] = f"Bearer {st.session_state.auth_token}"
    try:
        t0 = time.time()
        if method == "GET":
            response = requests.get(url, headers=hdrs, params=params, timeout=60)
        elif method == "POST":
            if endpoint == "/auth/token":
                response = requests.post(url, headers=hdrs, data=payload, timeout=30)
            elif files:
                response = requests.post(url, headers=hdrs, files=files, data=payload, timeout=180)
            else:
                response = requests.post(url, headers=hdrs, json=payload, timeout=180)
        elif method == "PATCH":
            response = requests.patch(url, headers=hdrs, json=payload, timeout=60)
        elif method == "DELETE":
            response = requests.delete(url, headers=hdrs, timeout=30)
        else:
            st.error(f"Unknown method: {method}")
            return
        lat = time.time() - t0
        sc  = response.status_code

        # Status badge
        if 200 <= sc < 300:
            badge = f"<span style='background:#2ecc71;color:white;padding:3px 12px;border-radius:12px;font-weight:bold'>✅ {sc}</span>"
        elif 400 <= sc < 500:
            badge = f"<span style='background:#f39c12;color:white;padding:3px 12px;border-radius:12px;font-weight:bold'>⚠️ {sc}</span>"
        else:
            badge = f"<span style='background:#e74c3c;color:white;padding:3px 12px;border-radius:12px;font-weight:bold'>❌ {sc}</span>"

        c1, c2, c3 = st.columns([2, 2, 4])
        c1.markdown(badge, unsafe_allow_html=True)
        c2.markdown(f"⏱ **{lat:.2f}s**")
        c3.markdown(f"`{method} {url}`")

        # cURL export
        is_form = endpoint == "/auth/token"
        with st.expander("📋 cURL Command"):
            st.code(_build_curl(method, url, hdrs, payload, is_form), language="bash")

        # Response body
        ct = response.headers.get("Content-Type", "")
        if "application/pdf" in ct or "application/octet-stream" in ct:
            st.success("Binary file returned.")
            st.download_button("⬇ Download", response.content, file_name=f"api_result_{int(t0)}.bin")
        else:
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text[:2000])

        # History
        st.session_state.api_history.append({"method": method, "endpoint": endpoint, "status": sc, "latency": lat})
        st.session_state.api_history = st.session_state.api_history[-20:]

    except Exception as e:
        st.error(f"❌ Request failed: {e}")
        st.session_state.api_history.append({"method": method, "endpoint": endpoint, "status": 0, "latency": 0.0})

def _ep(method, path, note=""):
    colours = {"POST": "method-post", "GET": "method-get", "PATCH": "method-patch", "DELETE": "method-delete"}
    colour_cls = colours.get(method, "")
    auth_html  = "<span class='auth-required'>🔐 auth</span>"  if note == "auth"  else ""
    admin_html = "<span class='admin-required'>👑 admin</span>" if note == "admin" else ""
    return st.markdown(
        f"<span class='endpoint-badge {colour_cls}'>{method}</span>"
        f"<span class='ep-path'>{path}</span>{auth_html}{admin_html}",
        unsafe_allow_html=True
    )
