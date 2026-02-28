import streamlit as st
import os

def render_smtp_tab():
    st.header("📧 SMTP Settings")
    st.info("Configure an external SMTP server to send real password reset emails. Leave blank to use Mock Mode (logs).")
    
    with st.form("smtp_config"):
        c1, c2 = st.columns(2)
        with c1:
            smtp_server = st.text_input("SMTP Server", value=os.environ.get("SMTP_SERVER", "smtp.gmail.com"))
            smtp_port = st.number_input("SMTP Port", value=int(os.environ.get("SMTP_PORT", 587)))
        with c2:
            smtp_sender = st.text_input("Sender Email", value=os.environ.get("SMTP_SENDER_EMAIL", ""))
        
        c3, c4 = st.columns(2)
        with c3:
            smtp_user = st.text_input("SMTP Username", value=os.environ.get("SMTP_USERNAME", ""))
        with c4:
            smtp_pass = st.text_input("SMTP Password", value=os.environ.get("SMTP_PASSWORD", ""), type="password")
            
        if st.form_submit_button("💾 Save SMTP Settings"):
            try:
                os.environ["SMTP_SERVER"] = smtp_server
                os.environ["SMTP_PORT"] = str(smtp_port)
                os.environ["SMTP_SENDER_EMAIL"] = smtp_sender
                os.environ["SMTP_USERNAME"] = smtp_user
                os.environ["SMTP_PASSWORD"] = smtp_pass
                
                from utils.dashboard_state import save_key_to_env
                save_key_to_env("SMTP_SERVER", smtp_server)
                save_key_to_env("SMTP_PORT", str(smtp_port))
                save_key_to_env("SMTP_SENDER_EMAIL", smtp_sender)
                save_key_to_env("SMTP_USERNAME", smtp_user)
                save_key_to_env("SMTP_PASSWORD", smtp_pass)
                
                st.success("SMTP Settings Saved! Restarting app...")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save settings: {e}")
