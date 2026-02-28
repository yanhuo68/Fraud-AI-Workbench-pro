import streamlit as st
from views.api_interaction.helpers import make_request, _ep

def render_auth_tab(api_base_url):
    col1, col2 = st.columns(2)

    with col1:
        _ep("POST", "/auth/token")
        st.caption("Login and get a JWT Bearer token.")
        with st.form("auth_login_form"):
            user = st.text_input("Username", value="yanhuo68")
            pw   = st.text_input("Password", type="password")
            if st.form_submit_button("🔐 Login", use_container_width=True):
                make_request("POST", "/auth/token", api_base_url, payload={"username": user, "password": pw})

        st.divider()
        _ep("POST", "/auth/register")
        st.caption("Register a new user account.")
        with st.form("auth_reg_form"):
            reg_u    = st.text_input("Username")
            reg_e    = st.text_input("Email (optional)", placeholder="user@example.com")
            reg_pw   = st.text_input("Password (min 8 chars)", type="password")
            reg_role = st.selectbox("Role", ["guest", "data_scientist", "admin"])
            if st.form_submit_button("📝 Register", use_container_width=True):
                make_request("POST", "/auth/register", api_base_url, payload={
                    "username": reg_u,
                    "email": reg_e if reg_e.strip() else None,
                    "password": reg_pw,
                    "role": reg_role
                })

        st.divider()
        _ep("POST", "/auth/forgot-password")
        st.caption("Trigger password reset email (or mock log if SMTP not configured).")
        with st.form("forgot_pw_form"):
            fp_email = st.text_input("Email address")
            if st.form_submit_button("📧 Send Reset Link", use_container_width=True):
                make_request("POST", "/auth/forgot-password", api_base_url, payload={"email": fp_email})

        _ep("POST", "/auth/reset-password")
        st.caption("Confirm reset using the token from the email link.")
        with st.form("reset_pw_form"):
            rp_token = st.text_input("Reset Token (from email link)")
            rp_new   = st.text_input("New Password", type="password")
            if st.form_submit_button("🔑 Reset Password", use_container_width=True):
                make_request("POST", "/auth/reset-password", api_base_url, payload={
                    "token": rp_token,
                    "new_password": rp_new
                })

    with col2:
        _ep("GET",    "/keys/")
        st.caption("List all active API keys. 🔐 auth required.")
        if st.button("List Keys", use_container_width=True, key="list_keys"):
            make_request("GET", "/keys/", api_base_url)

        st.divider()
        _ep("POST", "/keys/generate", "auth")
        st.caption("Generate a new named API key.")
        with st.form("key_gen_form"):
            k_name = st.text_input("Key Name", value="My Service Key")
            if st.form_submit_button("Generate Key", use_container_width=True):
                make_request("POST", "/keys/generate", api_base_url, payload={"name": k_name})

        st.divider()
        _ep("DELETE", "/keys/{id}", "admin")
        st.caption("Revoke an API key by ID.")
        k_id = st.number_input("Key ID to Revoke", min_value=1, step=1, key="revoke_kid")
        if st.button("Revoke Key", use_container_width=True, key="revoke_key_btn"):
            make_request("DELETE", f"/keys/{k_id}", api_base_url)
