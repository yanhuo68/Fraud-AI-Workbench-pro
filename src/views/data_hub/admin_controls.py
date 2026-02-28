import streamlit as st
import requests
from views.data_hub.utils import get_headers, API_URL

def render_admin_controls():
    is_admin = st.session_state.get("user") and st.session_state.user.get("role") == "admin"
    if not is_admin:
        return
        
    headers = get_headers()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ Admin Controls")
    
    if st.sidebar.button("Clean DB"):
        with st.spinner("Cleaning database..."):
            try:
                resp = requests.post(f"{API_URL}/admin/clean-db", headers=headers)
                if resp.status_code == 200:
                    st.success("Database cleaned successfully.")
                else:
                    st.error(f"Failed to clean DB: {resp.text}")
            except Exception as e:
                st.error(f"Error cleaning DB: {e}")

    if st.sidebar.button("Delete Uploads"):
        with st.spinner("Deleting uploaded files..."):
            try:
                resp = requests.post(f"{API_URL}/admin/delete-uploads", headers=headers)
                if resp.status_code == 200:
                    st.success("Uploaded files deleted successfully.")
                else:
                    st.error(f"Failed to delete uploads: {resp.text}")
            except Exception as e:
                st.error(f"Error deleting uploads: {e}")

    if st.sidebar.button("Rebuild Graph"):
        st.toast("🚀 Starting graph rebuild...", icon="🧪")
        with st.spinner("Rebuilding graph from uploads..."):
            try:
                resp = requests.post(f"{API_URL}/admin/rebuild-graph", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get('message', 'Graph rebuilt successfully')
                    st.success(msg)
                    st.toast(f"✅ {msg}", icon="🎉")
                else:
                    st.error(f"Failed to rebuild graph: {resp.text}")
                    st.toast("❌ Graph rebuild failed", icon="⚠️")
            except Exception as e:
                st.error(f"Error rebuilding graph: {e}")
                st.toast("🚨 Connection error during rebuild", icon="❌")

    if st.sidebar.button("Clean Graph"):
        with st.spinner("Deleting all graph nodes..."):
            try:
                resp = requests.post(f"{API_URL}/admin/delete-graph", headers=headers)
                if resp.status_code == 200:
                    st.success("Graph store cleaned successfully.")
                else:
                    st.error(f"Failed to clean graph: {resp.text}")
            except Exception as e:
                st.error(f"Error cleaning graph: {e}")

    if st.sidebar.button("Project Data to Graph"):
        st.sidebar.info("Projecting SQLite data to Neo4j...")
        try:
            resp = requests.post(f"{API_URL}/admin/project-data-to-graph", headers=headers)
            if resp.status_code == 200:
                result = resp.json()
                st.sidebar.success(f"Success! {result['stats']}")
            else:
                st.sidebar.error(f"Failed: {resp.text}")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
