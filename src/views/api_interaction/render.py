import streamlit as st
import logging
from config.settings import settings

from utils.dashboard_state import init_state
from components.sidebar import render_global_sidebar, enforce_page_access
from views.api_interaction.helpers import get_available_llms

from views.api_interaction.tab_auth import render_auth_tab
from views.api_interaction.tab_ingest import render_ingest_tab
from views.api_interaction.tab_intel import render_intel_tab
from views.api_interaction.tab_models import render_models_tab
from views.api_interaction.tab_admin import render_admin_tab
from views.api_interaction.tab_health import render_health_tab

logger = logging.getLogger(__name__)

def render_api_interaction():
    # Initialize State
    init_state()
    enforce_page_access("10_🔌_API_Interaction")
    render_global_sidebar()

    st.set_page_config(page_title="API Interaction Hub", page_icon="🔌", layout="wide")

    # ── Custom CSS ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
        .endpoint-badge {
            padding: 3px 10px; border-radius: 5px;
            font-family: monospace; font-weight: bold; font-size: 0.88rem;
            display: inline-block; margin-right: 6px;
        }
        .method-post   { background: #49cc90; color: white; }
        .method-get    { background: #61affe; color: white; }
        .method-patch  { background: #50e3c2; color: #333; }
        .method-delete { background: #f93e3e; color: white; }
        .ep-path { font-family: monospace; color: #e0e0e0; font-size: 0.9rem; }
        .auth-required { color: #f39c12; font-size: 0.78rem; margin-left:4px; }
        .admin-required { color: #e74c3c; font-size: 0.78rem; margin-left:4px; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔌 API Interaction Hub")
    st.caption("Live testing console for all Sentinel Pro FastAPI backend endpoints.")

    # ── Session state ────────────────────────────────────────────────────────────────
    if "api_history" not in st.session_state:
        st.session_state.api_history = []

    # ──────────────────────────────────────────────────────────────────────────────────
    # SIDEBAR CONFIGURATION
    # ──────────────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ API Configuration")
        api_base_url = st.text_input(
            "Base URL", value="http://fastapi:8000",
            help="URL of the FastAPI service within the Docker network."
        )
        if st.button("🔗 Check Connectivity", use_container_width=True):
            try:
                import requests
                resp = requests.get(f"{api_base_url}/health", timeout=5)
                if resp.status_code == 200:
                    st.success("✅ Connected to FastAPI!")
                    st.json(resp.json())
                else:
                    st.warning(f"⚠️ Status: {resp.status_code}")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

        st.divider()
        st.subheader("🤖 LLM Discovery")
        status = st.session_state.get("discovery_status", "Not Started")
        st.caption(f"Status: **{status}**")
        if st.button("🔄 Refresh Available LLMs", use_container_width=True):
            st.session_state.pop("available_llms", None)
            st.rerun()

        st.divider()
        st.subheader("📜 Request History")
        if st.session_state.api_history:
            if st.button("🗑 Clear History", use_container_width=True):
                st.session_state.api_history = []
                st.rerun()
            for entry in reversed(st.session_state.api_history[-12:]):
                _icon = "🟢" if entry["status"] in range(200, 300) else "🔴"
                st.caption(
                    f"{_icon} **{entry['method']}** `{entry['endpoint']}`  \n"
                    f"HTTP {entry['status']} · ⏱ {entry['latency']:.2f}s"
                )
        else:
            st.caption("No requests yet.")

    available_llms = get_available_llms(api_base_url)

    if not st.session_state.get("user"):
        st.warning("⚠️ Not logged in — authentication endpoints work, but most others require a Bearer token.")

    # ──────────────────────────────────────────────────────────────────────────────────
    # TABS
    # ──────────────────────────────────────────────────────────────────────────────────

    tabs = st.tabs(["🔒 Identity & Auth", "📁 Ingestion", "🧠 Intelligence", "🤖 ML Models", "📊 Admin & Infra", "🏥 Health"])
    
    with tabs[0]:
        render_auth_tab(api_base_url)
        
    with tabs[1]:
        render_ingest_tab(api_base_url)
        
    with tabs[2]:
        render_intel_tab(api_base_url, available_llms)
        
    with tabs[3]:
        render_models_tab(api_base_url, available_llms)
        
    with tabs[4]:
        render_admin_tab(api_base_url)
        
    with tabs[5]:
        render_health_tab(api_base_url)
