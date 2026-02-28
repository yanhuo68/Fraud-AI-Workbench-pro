import streamlit as st
import requests

def render_api_keys_tab(API_URL, headers):
    st.header("Technical API Keys")
    st.info("API Keys allow technical services (scripts, cron jobs) to interact with the FastAPI backend without a user session.")
    
    # Generate form
    with st.expander("➕ Generate New API Key", expanded=st.session_state.get("new_api_key_data") is not None):
        with st.form("gen_key", clear_on_submit=True):
            key_name = st.text_input("Name/Description", placeholder="e.g., Nightly Ingestion Script")
            submit = st.form_submit_button("Generate Key")
            
            if submit and key_name:
                try:
                    resp = requests.post(f"{API_URL}/keys/generate", json={"name": key_name}, headers=headers)
                    if resp.status_code == 200:
                        st.session_state.new_api_key_data = resp.json()
                        st.rerun()
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Show result outside form if it exists in session state
        new_key = st.session_state.get("new_api_key_data")
        if new_key:
            st.success(f"Key generated successfully!")
            st.code(new_key["key"], language="text")
            st.warning("⚠️ Copy this key now! It will not be shown again in full.")
            
            st.markdown("**Usage Example (curl):**")
            curl_cmd = f'curl -H "X-API-Key: {new_key["key"]}" {API_URL}/agents/query -d \'{{"question": "How many transactions?"}}\''
            st.code(curl_cmd, language="bash")
            
            col_dl, col_clr = st.columns([1, 1])
            with col_dl:
                st.download_button(
                    label="📥 Download as Shell Script",
                    data=f"#!/bin/bash\n{curl_cmd}\n",
                    file_name="test_fraud_api.sh",
                    mime="text/x-shellscript"
                )
            with col_clr:
                if st.button("♻️ Clear Result"):
                    st.session_state.new_api_key_data = None
                    st.rerun()

    # List keys
    st.subheader("Active Keys")
    try:
        resp = requests.get(f"{API_URL}/keys/", headers=headers)
        if resp.status_code == 200:
            keys = resp.json()
            if not keys:
                st.info("No API keys found.")
            else:
                st.caption(f"🔑 {len(keys)} active key(s) — full key shown only at generation time")
                for k in keys:
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    with col1:
                        st.write(f"**{k['name']}**")
                    with col2:
                        # ── NEW: mask key, show only last 8 chars ──────────────
                        _raw = k.get('key', '')
                        _masked = f"{'*' * (len(_raw) - 8)}...{_raw[-8:]}" if len(_raw) > 8 else _raw
                        st.code(_masked, language="text")
                        st.caption("💡 Full key was shown once at generation")
                    with col3:
                        st.caption(f"Created: {k['created_at']}")
                    with col4:
                        if st.button("🗑️", key=f"del_key_{k['id']}", help="Revoke this API key"):
                            try:
                                dresp = requests.delete(f"{API_URL}/keys/{k['id']}", headers=headers)
                                if dresp.status_code == 200:
                                    st.success("Revoked")
                                    st.rerun()
                                else:
                                    st.error("Failed")
                            except Exception:
                                st.error("Error")
        else:
            st.error("Failed to fetch keys.")
    except Exception as e:
        st.error(f"Error fetching keys: {e}")
