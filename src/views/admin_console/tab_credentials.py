import streamlit as st
import os
import requests

def render_credentials_tab():
    st.header("🔐 External Credentials")
    st.info("Manage API keys for external data sources (Kaggle, GitHub). Keys are saved to `.env` for persistence.")

    # ── KAGGLE ─────────────────────────────────────────────────────────────────
    st.subheader("Kaggle API")
    kag_user = st.text_input("Kaggle Username", value=os.environ.get("KAGGLE_USERNAME", ""), type="default")
    kag_key  = st.text_input("Kaggle Key", value=os.environ.get("KAGGLE_KEY", ""), type="password")

    _kag_c1, _kag_c2 = st.columns(2)
    if _kag_c1.button("💾 Save Kaggle Credentials", use_container_width=True):
        try:
            os.environ["KAGGLE_USERNAME"] = kag_user
            os.environ["KAGGLE_KEY"] = kag_key
            from utils.dashboard_state import save_key_to_env
            save_key_to_env("KAGGLE_USERNAME", kag_user)
            save_key_to_env("KAGGLE_KEY", kag_key)
            st.success("Kaggle credentials saved!")
        except Exception as e:
            st.error(f"Failed to save credentials: {e}")

    # ── NEW: Kaggle connection test ────────────────────────────────────────────
    if _kag_c2.button("🔬 Test Kaggle Connection", use_container_width=True):
        if not kag_user or not kag_key:
            st.warning("Enter Kaggle username and key first.")
        else:
            try:
                import json as _json
                _kag_resp = requests.get(
                    "https://www.kaggle.com/api/v1/competitions/list",
                    auth=(kag_user, kag_key), timeout=10
                )
                if _kag_resp.status_code == 200:
                    st.success(f"✅ Kaggle connection OK! (HTTP {_kag_resp.status_code})")
                elif _kag_resp.status_code == 401:
                    st.error("❌ Kaggle: Invalid credentials (401 Unauthorized)")
                else:
                    st.warning(f"⚠️ Kaggle responded with HTTP {_kag_resp.status_code}")
            except Exception as _e:
                st.error(f"❌ Could not reach Kaggle API: {_e}")

    st.markdown("---")

    # ── GITHUB ─────────────────────────────────────────────────────────────────
    st.subheader("GitHub API")
    gh_token = st.text_input("GitHub Token (Optional, for private repos/higher limits)", value=os.environ.get("GITHUB_TOKEN", ""), type="password")

    _gh_c1, _gh_c2 = st.columns(2)
    if _gh_c1.button("💾 Save GitHub Token", use_container_width=True):
        try:
            os.environ["GITHUB_TOKEN"] = gh_token
            from utils.dashboard_state import save_key_to_env
            save_key_to_env("GITHUB_TOKEN", gh_token)
            st.success("GitHub token saved!")
        except Exception as e:
            st.error(f"Failed to save token: {e}")

    # ── NEW: GitHub connection test ────────────────────────────────────────────
    if _gh_c2.button("🔬 Test GitHub Connection", use_container_width=True):
        try:
            _gh_headers = {"Authorization": f"token {gh_token}"} if gh_token else {}
            _gh_resp = requests.get("https://api.github.com/rate_limit", headers=_gh_headers, timeout=10)
            if _gh_resp.status_code == 200:
                _rl = _gh_resp.json().get("rate", {})
                _remaining = _rl.get("remaining", "?")
                _limit = _rl.get("limit", "?")
                st.success(f"✅ GitHub connection OK! Rate limit: {_remaining}/{_limit} requests remaining")
            elif _gh_resp.status_code == 401:
                st.error("❌ GitHub: Invalid token (401 Unauthorized)")
            else:
                st.warning(f"⚠️ GitHub responded with HTTP {_gh_resp.status_code}")
        except Exception as _e:
            st.error(f"❌ Could not reach GitHub API: {_e}")
