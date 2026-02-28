import streamlit as st
import time
import requests
from config.settings import settings
import logging
from utils.auth_utils import decode_access_token
from agents.llm_router import get_available_llms

logger = logging.getLogger(__name__)

def fetch_user_permissions(token: str = None):
    """Fetch permissions for the current user from the API if not already in session state."""
    if "user_permissions" not in st.session_state:
        st.session_state.user_permissions = None
        
    logger.info(f"fetch_user_permissions called. Current state: {st.session_state.get('user_permissions')}")
    
    # Fetch if permissions are None OR if we have a token but permissions are still empty (potentially stale from unauth context)
    target_token = token or st.session_state.get("auth_token")
    
    if st.session_state.user_permissions is None or (target_token and not st.session_state.user_permissions):
        if target_token:
            try:
                url = f"{settings.api_url}/admin/permissions"
                logger.info(f"Fetching permissions from: {url}")
                st.toast(f"🔍 Fetching perms from {settings.api_url}...", icon="📡")
                
                resp = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {target_token}"},
                    timeout=5
                )
                logger.info(f"Permissions API response: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.user_permissions = data.get("permissions", [])
                    st.session_state.auth_error = None
                    logger.info(f"Permissions fetched successfully: {len(st.session_state.user_permissions)} items")
                    st.toast("✅ Permissions loaded!", icon="🛡️")
                else:
                    st.session_state.user_permissions = []
                    try:
                        detail = resp.json().get("detail", "Permission fetch failed")
                        st.session_state.auth_error = f"API Error ({resp.status_code}): {detail}"
                    except:
                        st.session_state.auth_error = f"API Error ({resp.status_code})"
            except Exception as e:
                import traceback
                st.session_state.user_permissions = []
                st.session_state.auth_error = f"Connection failed: {str(e)}"
                logger.error(f"Permission fetch failed: {e}\n{traceback.format_exc()}")
        else:
            st.session_state.user_permissions = []
            
    return st.session_state.user_permissions or []

def apply_sentinel_theme():
    """Injects the global Sentinel premium theme CSS."""
    st.markdown("""
        <style>
            /* Global Background and Typography */
            .stApp {
                background: radial-gradient(circle at top right, #1a1a1a, #0d0d0d) !important;
                color: #e0e0e0 !important;
            }
            
            /* Glassmorphism Sidebar */
            [data-testid="stSidebar"] {
                background-color: rgba(15, 15, 15, 0.95) !important;
                backdrop-filter: blur(15px);
                border-right: 1px solid rgba(255, 75, 75, 0.2);
            }
            
            /* Global Sidebar Text Visibility */
            [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, 
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stCaption,
            [data-testid="stSidebar"] li {
                color: #ffffff !important;
            }
            
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3 {
                color: #ffffff !important;
            }
            
            /* Sidebar Logo High-Contrast Glow */
            [data-testid="stSidebar"] [data-testid="stImage"] img {
                filter: drop-shadow(0 0 12px rgba(255, 75, 75, 0.5)) !important;
                border-radius: 10px !important;
                transition: transform 0.3s ease !important;
            }
            [data-testid="stSidebar"] [data-testid="stImage"] img:hover {
                transform: scale(1.05);
                filter: drop-shadow(0 0 18px rgba(255, 75, 75, 0.7)) !important;
            }
            
            /* Glassmorphism Cards (used via markdown) */
            .glass-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.3s ease, border 0.3s ease;
            }
            .glass-card:hover {
                transform: translateY(-5px);
                border: 1px solid rgba(255, 75, 75, 0.4);
            }
            
            /* Primary Action Buttons (Crimson) */
            .stButton > button, 
            .stDownloadButton > button, 
            [data-testid="stFormSubmitButton"] > button {
                border-radius: 8px !important;
                background: linear-gradient(45deg, #ff4b4b, #8b0000) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
            }
            
            /* Secondary Action Buttons (Popovers / View Demo / Secondary) */
            div[data-testid="stPopover"] button,
            .stBaseButton-secondary,
            button[kind="secondary"] {
                background-color: #1c2833 !important;
                background: linear-gradient(135deg, #2c3e50 0%, #0d0d0d 100%) !important;
                color: #ffffff !important;
                border: 1px solid #4b4b4b !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3) !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.5rem 1rem !important;
            }
            div[data-testid="stPopover"] button:hover,
            .stBaseButton-secondary:hover,
            button[kind="secondary"]:hover {
                border-color: #ff4b4b !important;
                background: #2c3e50 !important;
                color: #ffffff !important;
            }

            /* Force Text/Icon color to White for all high-contrast buttons */
            button * {
                color: #ffffff !important;
            }

            /* --- INPUT & WIDGET STYLING --- */
            .stRadio label, 
            .stSelectbox label, 
            .stTextInput label, 
            .stNumberInput label, 
            .stSlider label,
            [data-testid="stWidgetLabel"] p {
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            [data-testid="stMarkdownContainer"] p {
                color: #ffffff !important;
            }
            .stSelectbox div[data-baseweb="select"] > div {
                color: #ffffff !important;
            }

            /* --- POPOVER & FORM THEMING (Login/Registration) --- */
            [data-testid="stPopoverContent"], 
            div[data-testid="stPopoverContent"] > div,
            .stPopoverContent {
                background-color: #1a1a1a !important;
                background: linear-gradient(135deg, #262626 0%, #0d0d0d 100%) !important;
                border: 1px solid rgba(255, 75, 75, 0.4) !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
                color: #ffffff !important;
            }
            [data-testid="stForm"], .stForm {
                background-color: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
                padding: 1.5rem !important;
            }
            [data-testid="stForm"] [data-testid="stMarkdownContainer"] p {
                color: #ffffff !important;
            }
            [data-testid="stPopoverContent"] button[kind="secondaryFormSubmit"],
            button[data-testid="baseButton-secondaryFormSubmit"] {
                background: linear-gradient(45deg, #ff4b4b, #8b0000) !important;
                color: white !important;
                border: none !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
            }
            
            /* Input transparency and high contrast in forms */
            [data-testid="stForm"] input {
                background-color: rgba(0,0,0,0.4) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
            }
            [data-testid="stForm"] input:focus {
                border-color: #ff4b4b !important;
                box-shadow: 0 0 10px rgba(255,75,75,0.3) !important;
            }

            /* --- ALERT & NOTIFICATION STYLING --- */
            [data-testid="stAlert"] {
                background-color: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(5px);
                border-radius: 10px !important;
                color: #ffffff !important;
            }
            [data-testid="stAlert"][dir="ltr"]:has(div[role="alert"]:has(svg[data-testid="stIconInfo"])) {
                border-left: 5px solid #00d4ff !important;
                background-color: rgba(0, 212, 255, 0.1) !important;
            }
            [data-testid="stAlert"][dir="ltr"]:has(div[role="alert"]:has(svg[data-testid="stIconWarning"])) {
                border-left: 5px solid #ffd700 !important;
                background-color: rgba(255, 215, 0, 0.1) !important;
            }
            [data-testid="stAlert"][dir="ltr"]:has(div[role="alert"]:has(svg[data-testid="stIconError"])) {
                border-left: 5px solid #ff4b4b !important;
                background-color: rgba(255, 75, 75, 0.1) !important;
            }
            [data-testid="stAlert"][dir="ltr"]:has(div[role="alert"]:has(svg[data-testid="stIconSuccess"])) {
                border-left: 5px solid #00ff88 !important;
                background-color: rgba(0, 255, 136, 0.1) !important;
            }
            [data-testid="stAlert"] * {
                color: #ffffff !important;
            }

            /* Page Links */
            [data-testid="stPageLink"] {
                background: rgba(255, 255, 255, 0.05) !important;
                border: 1px solid rgba(255, 75, 75, 0.2) !important;
                border-radius: 8px !important;
                padding: 8px !important;
                transition: all 0.3s ease !important;
            }
            [data-testid="stPageLink"]:hover {
                background: rgba(255, 75, 75, 0.15) !important;
                border-color: #ff4b4b !important;
            }
            [data-testid="stPageLink"] p, [data-testid="stPageLink"] div {
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            
            /* Headers */
            h1, h2, h3 {
                color: #ffffff !important;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            }
        </style>
    """, unsafe_allow_html=True)

def _run_demo_installer_ui(api_url: str):
    """Render the Quick Install Demo Data catalogue + progress in the main area."""
    from utils.demo_installer import DEMO_CATALOGUE, install_demo_data, is_demo_already_installed

    if is_demo_already_installed():
        st.success("✅ Demo data was already installed. Log in with one of the demo accounts below.")
        for user_line in DEMO_CATALOGUE.get("👥 Users Created", []):
            st.markdown(f"- {user_line}")
        return

    st.subheader("📦 What will be installed?")
    for section, items in DEMO_CATALOGUE.items():
        with st.expander(section, expanded=True):
            for item in items:
                st.markdown(f"- {item}")

    st.warning(
        "⚠️ **Security note:** The admin account `yanhuo68` will be created with a "
        "known default password. Please change it immediately after first login. "
        "The Quick Install button will be **auto-disabled** after installation."
    )

    col_yes, col_no = st.columns(2)
    if col_yes.button("🚀 Confirm Install Demo Data", type="primary", use_container_width=True):
        log_container = st.empty()
        progress_bar  = st.progress(0)
        log_lines     = []

        def _cb(step, total, message, ok):
            progress_bar.progress(step / total)
            log_lines.append(message)
            log_container.markdown("\n\n".join(log_lines))

        with st.spinner("Installing demo data… this may take 30–60 seconds"):
            result = install_demo_data(api_url, progress_callback=_cb)

        if result["success"]:
            st.balloons()
            st.success("🎉 Demo data installed! You can now log in with any of the demo accounts.")
            st.rerun()
        else:
            st.error("Some steps failed — see log above. You may retry or log in manually.")

    if col_no.button("Cancel", use_container_width=True):
        st.session_state["_show_demo_installer"] = False
        st.rerun()


def enforce_page_access(page_id: str):
    """Enforce access control for a specific page."""
    from utils.demo_installer import is_demo_button_enabled
    from config.settings import settings as _settings

    # Apply theme even if we stop
    apply_sentinel_theme()

    # Home is always accessible
    if page_id == "home":
        return

    # ── Not logged in → full onboarding auth-wall ─────────────────────────────
    if not st.session_state.get("user"):

        # ── Hero banner ───────────────────────────────────────────────────────
        st.markdown(f"""
            <div style="padding: 2.5rem; background: linear-gradient(135deg, #4b0000 0%, #0d0d0d 100%);
                        border-radius: 20px; border: 1px solid #ff4b4b; margin-top: 2rem; text-align: center;">
                <h1 style='color: white; margin-bottom: 0.5rem;'>🔑 Authentication Required</h1>
                <p style='font-size: 1.25rem; color: #f0f0f0;'>
                    Please login to access the <b>{page_id}</b> intelligence portal.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # ── Row 1: navigation buttons (always 3, never cramped) ─────────────────
        _demo_enabled = is_demo_button_enabled()
        _r1_c1, _r1_c2, _r1_c3 = st.columns(3)

        if _r1_c1.button("🏠 Back to Portal", use_container_width=True):
            st.switch_page("app.py")

        if _r1_c2.button("🔐 Login", type="primary", use_container_width=True):
            st.session_state["_authwall_mode"] = "login"
            st.rerun()

        if _r1_c3.button("📝 Register", use_container_width=True):
            st.session_state["_authwall_mode"] = "register"
            st.rerun()

        # ── Row 2: Quick Install (full-width, green, only when enabled) ──────────
        if _demo_enabled:
            st.markdown("""
            <style>
            /* Green button: sidebar Quick Install is :last-of-type;
               auth-wall Quick Install sits alone in a full-width row */
            [data-testid="stButton"]:last-of-type button {
                background: linear-gradient(135deg, #1a7a3c 0%, #22a44e 100%) !important;
                color: #ffffff !important;
                border: 1px solid #27ae60 !important;
                font-weight: 700 !important;
                font-size: 1.0rem !important;
                box-shadow: 0 0 18px rgba(34,164,78,0.6) !important;
                transition: box-shadow 0.25s ease, background 0.25s ease !important;
                padding: 0.65rem 1rem !important;
            }
            [data-testid="stButton"]:last-of-type button:hover {
                background: linear-gradient(135deg, #22a44e 0%, #2ecc71 100%) !important;
                box-shadow: 0 0 32px rgba(34,164,78,0.95) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            _demo_clicked = st.button(
                "⚡ Quick Install Demo Data — one-click setup for new users",
                use_container_width=True,
                key="aw_quick_demo"
            )
            if _demo_clicked:
                st.session_state["_authwall_mode"] = "demo_install"
                st.rerun()

        st.markdown("---")


        # ── Mode-dependent inline forms ───────────────────────────────────────
        _mode = st.session_state.get("_authwall_mode", "")

        if _mode == "login":
            st.subheader("🔐 Login")
            with st.form("authwall_login_form"):
                _u = st.text_input("Username")
                _p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if not _u or not _p:
                        st.warning("Enter username and password.")
                    else:
                        try:
                            _resp = requests.post(
                                f"{_settings.api_url}/auth/token",
                                data={"username": _u, "password": _p},
                                timeout=10,
                            )
                            if _resp.status_code == 200:
                                from utils.auth_utils import decode_access_token
                                _data = _resp.json()
                                st.session_state.auth_token = _data["access_token"]
                                _payload = decode_access_token(_data["access_token"])
                                st.session_state.user = {"username": _u, "role": _payload.get("role", "guest")}
                                st.session_state["_authwall_mode"] = ""
                                st.session_state.user_permissions = None  # force refresh
                                st.success(f"Welcome back, {_u}! Redirecting to Home…")
                                # Redirect to Home — don't stay on the protected page
                                st.switch_page("app.py")
                            else:
                                st.error("Invalid credentials. Try again or use Register.")
                        except Exception as _e:
                            st.error(f"Connection error: {_e}")

        elif _mode == "register":
            st.subheader("📝 Register")
            st.info("New accounts are created with **guest** role. Ask an admin to upgrade your access.")
            with st.form("authwall_reg_form"):
                _ru = st.text_input("Username")
                _re = st.text_input("Email (optional)")
                _rp = st.text_input("Password", type="password")
                _rp2 = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not _ru or not _rp:
                        st.warning("Username and password are required.")
                    elif _rp != _rp2:
                        st.error("Passwords do not match.")
                    elif len(_rp) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            _resp = requests.post(
                                f"{_settings.api_url}/auth/register",
                                json={"username": _ru, "password": _rp, "email": _re, "role": "guest"},
                                timeout=10,
                            )
                            if _resp.status_code == 200:
                                st.success("✅ Account created! Click **🔐 Login** above to sign in.")
                                st.session_state["_authwall_mode"] = "login"
                                st.rerun()
                            else:
                                st.error(_resp.json().get("detail", "Registration failed."))
                        except Exception as _e:
                            st.error(f"Connection error: {_e}")

        elif _mode == "demo_install":
            _run_demo_installer_ui(_settings.api_url)

        st.stop()

    # ── Logged in but page not in permissions ─────────────────────────────────
    permissions = fetch_user_permissions()
    if page_id not in permissions:
        st.markdown(f"""
            <div style="padding: 2.5rem; background: linear-gradient(135deg, #2c3e50 0%, #1a1a1a 100%);
                        border-radius: 20px; border: 1px solid #ff4b4b; margin-top: 2rem; text-align: center;">
                <h1 style='color: white; margin-bottom: 0.5rem;'>🚫 Access Restricted</h1>
                <p style='font-size: 1.25rem; color: #f0f0f0;'>
                    Your current identity (<b>{st.session_state.user.get('role')}</b>) is not authorized
                    for <b>{page_id}</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.warning("Please contact your Sentinel Administrator to request advanced Clearance levels.")

        if st.button("🏠 Back to Home"):
            st.switch_page("app.py")
        st.stop()

# ── Help & Documents helpers ──────────────────────────────────────────────────

def _get_all_docs() -> dict:
    """Discover all documentation markdown files.
    Returns {display_label: absolute_file_path_str} ordered by category.
    """
    from pathlib import Path as _P
    # Sidebar is now in src/components, so root is 2 levels up
    docs_root = _P(__file__).parent.parent.parent / "documentation"
    result = {}

    # User manuals
    manual_dir = docs_root / "user_manual"
    if manual_dir.exists():
        for f in sorted(manual_dir.glob("*.md")):
            label = f"📋 {f.stem.replace('_', ' ')}"
            result[label] = str(f)

    # UI design specs
    design_dir = docs_root / "ui_design"
    if design_dir.exists():
        for f in sorted(design_dir.glob("*.md")):
            label = f"🎨 {f.stem.replace('_', ' ')}"
            result[label] = str(f)

    # References folder (CONFIGURATION_GUIDE, DEPENDENCY_REFERENCE, NEO4J_SETUP, etc.)
    ref_dir = docs_root / "references"
    if ref_dir.exists():
        for f in sorted(ref_dir.glob("*.md")):
            label = f"📦 {f.stem.replace('_', ' ')}"
            result[label] = str(f)

    return result


def _render_help_content(file_path: str):
    """Render a documentation markdown file in the main content area."""
    from pathlib import Path as _P
    path = _P(file_path)

    # ── Header row ────────────────────────────────────────────────────────────
    col_title, col_close = st.columns([9, 1])
    with col_title:
        st.subheader(f"📄 {path.stem.replace('_', ' ')}")
        st.caption(f"📁 `{file_path}`")
    with col_close:
        st.write("")
        if st.button("✖ Close", key="help_close_btn", type="secondary"):
            st.session_state["_help_doc_path"] = None
            st.session_state["_help_doc_open"] = False
            # Reset the sidebar selectbox so it returns to placeholder
            st.session_state.pop("sb_help_doc_selector", None)
            st.rerun()

    st.divider()

    # ── Document content ──────────────────────────────────────────────────────
    try:
        content = path.read_text(encoding="utf-8")
        st.markdown(content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"❌ Document not found: `{file_path}`")
    except Exception as exc:
        st.error(f"❌ Error reading document: {exc}")


def render_global_sidebar():
    """
    Renders the global sidebar configuration, including LLM selection.
    """
    # Apply global premium theme
    apply_sentinel_theme()
    
    # Always ensure permissions are fresh at the start of the sidebar run
    permissions = fetch_user_permissions()
    
    with st.sidebar:
        # --- SENTINEL BRANDING ---
        col1, col2 = st.columns([1, 4])
        with col1:
            try:
                # Increased width for the high-contrast premium brand mark
                st.image("data/assets/logo.png", width=60)
            except:
                st.markdown("<h1 style='margin:0; text-shadow: 0 0 10px rgba(255,75,75,0.5);'>🛡️</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h1 style='margin-bottom:0; padding-top:0; color:#ff4b4b;'>SENTINEL</h1>", unsafe_allow_html=True)
            st.caption("Fraud Detection AI Workbench")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎬 Show Demo", type="primary", use_container_width=True, help="Take an interactive visual tour of the platform features"):
            st.session_state.show_demo_overlay = True
            st.rerun()
        
        st.divider()

        st.header("👤 User Session")
        
        user = st.session_state.get("user")
        if user:
            st.markdown(f"**Logged in as:** {user['username']}")
            st.caption(f"🎭 Role: {user['role']}")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.auth_token = None
                st.session_state.user_permissions = None
                st.query_params.clear() # Clear any reset tokens
                st.success("Logged out safely.")
                st.session_state.show_demo_overlay = False
                st.rerun()
        else:
            # Check for Reset Token in URL
            qp = st.query_params
            reset_token = qp.get("reset_token")
            
            if reset_token:
                st.warning("🔐 Reset Password Mode")
                with st.form("reset_pw_form"):
                    new_p1 = st.text_input("New Password", type="password")
                    new_p2 = st.text_input("Confirm Password", type="password")
                    submitted = st.form_submit_button("Reset Password")
                    
                    if submitted:
                        if new_p1 != new_p2:
                            st.error("Passwords do not match")
                        elif len(new_p1) < 8:
                            st.error("Password must be 8+ chars")
                        else:
                            try:
                                resp = requests.post(f"{settings.api_url}/auth/reset-password", json={"token": reset_token, "new_password": new_p1})
                                if resp.status_code == 200:
                                    st.success("Password reset! Please log in.")
                                    time.sleep(2)
                                    st.query_params.clear()
                                    st.rerun()
                                else:
                                    st.error(resp.json().get("detail", "Failed"))
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                if st.button("Cancel Reset"):
                    st.query_params.clear()
                    st.rerun()

            else:
                st.warning("⚠️ Not Logged In")
                
                # Auth Modes
                mode = st.radio("Mode", ["Login", "Register", "Forgot Password"], horizontal=True, label_visibility="collapsed", key="sb_auth_mode_radio")
                
                if mode == "Login":
                    with st.form("sb_login_form"):
                        u = st.text_input("Username")
                        p = st.text_input("Password", type="password")
                        submitted = st.form_submit_button("Login", use_container_width=True)
                        
                        if submitted:
                            if not u or not p:
                                st.warning("Enter credentials")
                            else:
                                try:
                                    resp = requests.post(
                                        f"{settings.api_url}/auth/token",
                                        data={"username": u, "password": p},
                                        timeout=10
                                    )
                                    if resp.status_code == 200:
                                        data = resp.json()
                                        st.session_state.auth_token = data["access_token"]
                                        payload = decode_access_token(data["access_token"])
                                        st.session_state.user = {"username": u, "role": payload.get("role", "guest")}
                                        st.session_state.user_permissions = None  # Force fresh permission fetch
                                        st.success(f"Welcome, {u}!")
                                        st.rerun()
                                    else:
                                        st.error("Invalid credentials")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
                elif mode == "Register":
                     with st.form("sb_reg_form"):
                        u = st.text_input("New Username")
                        email = st.text_input("Email Address")
                        p = st.text_input("New Password", type="password")
                        submitted = st.form_submit_button("Register", use_container_width=True)
                        
                        if submitted:
                            if not u or not p or not email:
                                st.warning("All fields required")
                            else:
                                try:
                                    resp = requests.post(
                                        f"{settings.api_url}/auth/register",
                                        json={"username": u, "password": p, "email": email, "role": "guest"},
                                        timeout=10
                                    )
                                    if resp.status_code == 200:
                                        st.success("Registered! Switch to Login.")
                                    else:
                                        st.error(resp.json().get("detail", "Failed"))
                                except Exception as e:
                                    st.error(f"Error: {e}")

                elif mode == "Forgot Password":
                    st.info("Enter your registered email to receive a reset link.")
                    with st.form("sb_forgot_form"):
                        email = st.text_input("Email Address")
                        submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
                        
                        if submitted:
                            if not email:
                                st.error("Email required")
                            else:
                                try:
                                    resp = requests.post(f"{settings.api_url}/auth/forgot-password", json={"email": email})
                                    if resp.status_code == 200:
                                        st.success("If valid, link sent (Check Logs in Dev)")
                                    else:
                                        st.error("Failed")
                                except Exception as e:
                                    st.error(f"Error: {e}")

        st.divider()
        st.header("⚙️ Global Configuration")

        with st.expander("🔑 API Keys", expanded=False):
            st.text_input("OpenAI API Key", type="password", key="sidebar_openai_key", help="Overrides system environment")
            st.text_input("DeepSeek API Key", type="password", key="sidebar_deepseek_key", help="Overrides system environment")
            st.text_input("Google API Key", type="password", key="sidebar_google_key", help="Overrides system environment")
            st.text_input("Anthropic API Key", type="password", key="sidebar_anthropic_key", help="Overrides system environment")
            st.caption("Notice: Local session-based overrides.")
        
        # LLM Selection
        from agents.llm_router import get_available_llms
        if "available_llms" not in st.session_state:
            st.session_state["available_llms"] = get_available_llms(include_local=False)
        
        # Determine default index (e.g., gpt-4o-mini if available)
        default_idx = 0
        if "openai:gpt-4o-mini" in st.session_state["available_llms"]:
            default_idx = st.session_state["available_llms"].index("openai:gpt-4o-mini")
        
        col_llm, col_llm_ref = st.columns([4, 1])
        with col_llm:
            selected_llm = st.selectbox(
                "Select Active LLM",
                st.session_state["available_llms"],
                index=default_idx if default_idx < len(st.session_state["available_llms"]) else 0,
                key="sb_global_llm"
            )
        with col_llm_ref:
            st.write("") # padding
            if st.button("🔄", key="btn_scan_global_llm", help="Scan for local LLMs (Ollama/LM Studio)"):
                with st.spinner("Scanning..."):
                    st.session_state["available_llms"] = get_available_llms(include_local=True)
                    st.rerun()
        
        # Persist to session state
        st.session_state.global_llm_id = selected_llm
        
        st.divider()
        st.caption(f"Active Model: **{selected_llm}**")

        # --- Task Notification Hub ---
        st.markdown("---")
        st.subheader("🔔 Task Notification Hub")
        
        if "active_tasks" not in st.session_state:
            st.session_state.active_tasks = {}
            
        if not st.session_state.active_tasks:
            st.info("No active background tasks.")
        else:
            for task_id, task_info in list(st.session_state.active_tasks.items()):
                with st.expander(f"{task_info['emoji']} {task_info['name']}", expanded=True):
                    status = task_info.get("status", "running")
                    if status == "running":
                        st.write("Status: ⏳ In Progress...")
                        # Simulate progress if not provided
                        progress = task_info.get("progress", 0)
                        st.progress(progress)
                    elif status == "completed":
                        st.write("Status: ✅ Complete!")
                        st.success(task_info.get("result", "Finished successfully."))
                        if st.button("Dismiss", key=f"dismiss_{task_id}"):
                            del st.session_state.active_tasks[task_id]
                            st.rerun()
                    elif status == "failed":
                        st.write("Status: ❌ Failed")
                        st.error(task_info.get("error", "An error occurred."))
                        if st.button("Dismiss", key=f"dismiss_{task_id}"):
                            del st.session_state.active_tasks[task_id]
                            st.rerun()

        if st.session_state.get("user") and st.session_state.user.get("role") == "admin":
            st.caption("🛡️ Admin Session Active")
            
        # Temporary Debug info
        if st.session_state.get("user"):
            role = st.session_state.user.get('role', 'none')
            perms = st.session_state.get('user_permissions')
            st.caption(f"🔧 Debug: Role={role}, Perms={len(perms) if perms else 'None'}")
            if st.session_state.get("auth_error"):
                st.error(f"⚠️ {st.session_state.auth_error}")

        st.markdown("---")
        st.subheader("🚀 Navigation")
        # permissions already fetched at top of function
        pages = [
            {"label": "🏠 Home", "path": "app.py", "id": "home"},
            {"label": "📁 Data Hub", "path": "pages/1_📁_Data_Hub.py", "id": "1_📁_Data_Hub"},
            {"label": "🧠 SQL RAG", "path": "pages/2_🧠_SQL_RAG_Assistant.py", "id": "2_🧠_SQL_RAG_Assistant"},
            {"label": "🕸️ Graph RAG", "path": "pages/3_🕸️_Graph_RAG_Assistant.py", "id": "3_🕸️_Graph_RAG_Assistant"},
            {"label": "🎥 Multimodal RAG", "path": "pages/4_🎥_Multimodal_RAG_Assistant.py", "id": "4_🎥_Multimodal_RAG_Assistant"},
            {"label": "📈 Trends", "path": "pages/5_📈_Trends_and_Insights.py", "id": "5_📈_Trends_and_Insights"},
            {"label": "🔄 ML Workflow", "path": "pages/6_🔄_ML_Workflow.py", "id": "6_🔄_ML_Workflow"},
            {"label": "🧠 LLM Fine Tuning", "path": "pages/9_🧠_LLM_Fine_Tuning.py", "id": "9_🧠_LLM_Fine_Tuning"},
            {"label": "🔌 API Hub", "path": "pages/10_🔌_API_Interaction.py", "id": "10_🔌_API_Interaction"},
            {"label": "🛡️ Admin Console", "path": "pages/11_🛡️_Admin_Console.py", "id": "11_🛡️_Admin_Console"},
        ]
        
        for p in pages:
            if p["id"] == "home" or p["id"] in permissions:
                st.page_link(p["path"], label=p["label"])
            else:
                # Optionally show disabled links or nothing
                # st.caption(f"🔒 {p['label']}")
                pass

        # ── Help & Documents ─────────────────────────────────────────────────
        st.markdown("---")
        with st.expander("📚 Help & Documents", expanded=False):
            _help_docs = _get_all_docs()
            if _help_docs:
                _help_labels = ["— select a document —"] + list(_help_docs.keys())
                _help_chosen = st.selectbox(
                    "docs",
                    _help_labels,
                    key="sb_help_doc_selector",
                    label_visibility="collapsed",
                )
                if _help_chosen and _help_chosen != "— select a document —":
                    _chosen_path = _help_docs[_help_chosen]
                    if st.session_state.get("_help_doc_path") != _chosen_path:
                        st.session_state["_help_doc_path"] = _chosen_path
                        st.session_state["_help_doc_open"] = True
                elif _help_chosen == "— select a document —":
                    st.session_state["_help_doc_open"] = False
                    st.session_state["_help_doc_path"] = None

                if st.session_state.get("_help_doc_open"):
                    _viewing = st.session_state.get("_help_doc_path", "")
                    import os as _os
                    _stem = _os.path.basename(_viewing).replace(".md", "").replace("_", " ")
                    st.caption(f"📖 Viewing: {_stem}")
                    if st.button(
                        "✖ Close Help & Documents",
                        key="sb_help_close_btn",
                        use_container_width=True,
                    ):
                        st.session_state["_help_doc_path"] = None
                        st.session_state["_help_doc_open"] = False
                        st.session_state.pop("sb_help_doc_selector", None)
                        st.rerun()
            else:
                st.info("No documentation files found.")

        
        # ── NEW: Quick Install Demo Data sidebar button (green, contextual) ─────
        try:
            from utils.demo_installer import is_demo_button_enabled, is_demo_already_installed
            _demo_btn_enabled = is_demo_button_enabled()
            _demo_installed   = is_demo_already_installed()
        except Exception:
            _demo_btn_enabled = False
            _demo_installed   = False

        if _demo_btn_enabled and not user:  # only show when user is NOT logged in
            st.markdown("---")
            # Inject CSS using :has() — targets the Quick Install button by its unique text
            # This is the most reliable Streamlit button styling approach (no class/id needed)
            st.markdown("""
                <style>
                /* Target the last stButton in the sidebar (the Quick Install btn) */
                [data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button {
                    background: linear-gradient(135deg, #1a7a3c 0%, #22a44e 100%) !important;
                    color: #ffffff !important;
                    border: 1px solid #27ae60 !important;
                    font-weight: 700 !important;
                    box-shadow: 0 0 18px rgba(34, 164, 78, 0.6) !important;
                    transition: box-shadow 0.25s ease, background 0.25s ease !important;
                    letter-spacing: 0.3px !important;
                }
                [data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button:hover {
                    background: linear-gradient(135deg, #22a44e 0%, #2ecc71 100%) !important;
                    box-shadow: 0 0 30px rgba(34, 164, 78, 0.95) !important;
                }
                </style>
                <p style='color:#22a44e; font-size:0.82rem; text-align:center;
                          margin-bottom:4px; font-weight:600; letter-spacing:0.3px;'>
                    ✨ First time? Set up instantly!
                </p>
            """, unsafe_allow_html=True)
            _sb_demo_clicked = st.button(
                "⚡ Quick Install Demo Data",
                use_container_width=True,
                help="Creates demo users and loads sample fraud data in one click.",
                key="sb_quick_demo_install"
            )
            if _sb_demo_clicked:
                st.session_state["_trigger_demo_install_home"] = True
                st.switch_page("app.py")

        # Custom CSS to hide the default Streamlit sidebar page navigation
        st.markdown("""
            <style>
                [data-testid="stSidebarNav"] {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)

    # ── Full-screen Demo Viewer Hijack ──────────────────────────────────────────
    if st.session_state.get("show_demo_overlay", False):
        from components.demo_viewer import render_demo_viewer
        render_demo_viewer()
        st.stop()  # Immediately stop page execution, hiding the underlying page content

    # ── Render selected help document in main content area ────────────────────
    # This runs OUTSIDE `with st.sidebar:` so content appears in the page body.
    if st.session_state.get("_help_doc_open") and st.session_state.get("_help_doc_path"):
        _render_help_content(st.session_state["_help_doc_path"])
        st.stop()  # Suppress the actual page content while doc is open
