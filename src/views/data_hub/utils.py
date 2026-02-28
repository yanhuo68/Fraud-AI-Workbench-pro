import streamlit as st
import requests
from config.settings import settings

API_URL = settings.api_url

def get_headers():
    headers = {}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers

def auto_rebuild():
    with st.status("🛠️ **Auto-Syncing Data Hub...**", expanded=True) as status:
        st.write("Updating Graph Store & Knowledge Base...")
        try:
            resp = requests.post(f"{API_URL}/admin/rebuild-graph", headers=get_headers())
            if resp.status_code == 200:
                st.write("✅ Rebuild Complete.")
                status.update(label="🚀 **Data Hub Unified Successfully!**", state="complete", expanded=True)
                st.toast("Unified Successfully!", icon="🎉")
                return True
            else:
                st.error(f"Rebuild failed: {resp.text}")
                return False
        except Exception as e:
            st.error(f"Error during rebuild: {e}")
            return False
