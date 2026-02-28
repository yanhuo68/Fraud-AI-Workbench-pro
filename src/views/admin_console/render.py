import streamlit as st
import requests
import os
from components.sidebar import render_global_sidebar, enforce_page_access
from utils.dashboard_state import init_state
from config.settings import settings

from views.admin_console.tab_api_keys import render_api_keys_tab
from views.admin_console.tab_users import render_users_tab
from views.admin_console.tab_roles import render_roles_tab
from views.admin_console.tab_credentials import render_credentials_tab
from views.admin_console.tab_llms import render_llms_tab
from views.admin_console.tab_system_stats import render_system_stats_tab
from views.admin_console.tab_smtp import render_smtp_tab

def render_admin_console():
    # Initialize session state
    init_state()
    enforce_page_access("11_🛡️_Admin_Console")
    render_global_sidebar()

    API_URL = settings.api_url

    st.set_page_config(page_title="Admin Console", page_icon="🛡️", layout="wide")

    # Get auth headers
    headers = {}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

    user = st.session_state.get("user")
    is_admin = user and user.get("role") == "admin"

    if not is_admin:
        st.error("🚫 Access Denied. Admin privileges required.")
        st.info("Please use the **🔑 Authentication** section in the sidebar to login with an administrator account.")
        if st.button("🏠 Back to Home"):
            st.session_state.highlight_login = True
            st.switch_page("app.py")
        st.stop()

    st.title("🛡️ Admin Console")
    st.markdown("Centralized management for Fraud Lab security and system settings.")

    tabs = st.tabs(["🔑 API Keys", "👥 User Management", "🎭 Role Management", "🔐 External Credentials", "🤖 Local LLMs", "⚙️ System Stats", "📧 SMTP Settings"])

    with tabs[0]:
        render_api_keys_tab(API_URL, headers)
        
    with tabs[1]:
        render_users_tab(API_URL, headers)
        
    with tabs[2]:
        render_roles_tab(API_URL, headers)
        
    with tabs[3]:
        render_credentials_tab()
        
    with tabs[4]:
        render_llms_tab()
        
    with tabs[5]:
        render_system_stats_tab(API_URL, headers)
        
    with tabs[6]:
        render_smtp_tab()
