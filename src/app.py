import streamlit as st
import requests
from components.sidebar import render_global_sidebar, fetch_user_permissions
from agents.app_guide_agent import AppGuideAgent
from config.settings import settings
from utils.auth_utils import decode_access_token
from utils.dashboard_state import init_state
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

init_state()

st.set_page_config(
    page_title="Fraud Detection AI Workbench",
    page_icon="🛡️",
    layout="wide",
)

API_URL = settings.api_url
headers = {}
if st.session_state.get("auth_token"):
    headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

# ─────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 2.5rem 3rem; background: linear-gradient(135deg, #4b0000 0%, #1a1a1a 60%, #0a1a2e 100%);
     border-radius: 20px; border-left: 8px solid #ff4b4b; margin-bottom: 1.5rem;
     box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <h1 style='color: white; font-size: 3.5rem; margin: 0 0 0.3rem 0; letter-spacing: 4px;'>SENTINEL</h1>
    <h3 style='color: #ff4b4b; margin: 0 0 1rem 0; opacity: 0.95;'>Fraud Detection AI Workbench · Pro Edition</h3>
    <p style='color: #aaa; margin: 0; max-width: 780px; font-size: 1rem; line-height: 1.6;'>
        An end-to-end AI-powered platform for fraud investigation — combining <b style="color:#ddd;">SQL intelligence</b>,
        <b style="color:#ddd;">graph analytics</b>, <b style="color:#ddd;">multimodal AI</b>,
        <b style="color:#ddd;">ML experimentation</b>, <b style="color:#ddd;">real-time knowledge retrieval</b>,
        and <b style="color:#ddd;">one-click demo onboarding</b>.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GUEST PROMO BANNER (not logged in)
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.user:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34,164,78,0.12) 0%, rgba(255,75,75,0.07) 100%);
         border: 1px solid rgba(34,164,78,0.45); border-radius: 14px; padding: 1.25rem 2rem;
         text-align: center; margin-bottom: 1.5rem;">
        <h3 style="color: #22a44e; margin: 0 0 0.4rem 0;">⚡ Get Started in 30 Seconds</h3>
        <p style="color: #ccc; margin: 0; font-size: 1rem; line-height: 1.6;">
            New here? Click <b style="color:#2ecc71;">⚡ Quick Install Demo Data</b> in the sidebar to auto-create
            demo accounts, load fraud datasets, and set up the full environment in one click.<br>
            Already have an account? <b style="color:#aaa;">Login</b> or <b style="color:#aaa;">Register</b>
            via the sidebar to access all investigative tools.
        </p>
    </div>
    """, unsafe_allow_html=True)

render_global_sidebar()

# ─────────────────────────────────────────────────────────────────────────────
# QUICK INSTALL DEMO DATA — triggered from sidebar button when not logged in
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.pop("_trigger_demo_install_home", False):
    st.session_state["_home_show_demo"] = True

if st.session_state.get("_home_show_demo") and not st.session_state.get("user"):
    from components.sidebar import _run_demo_installer_ui
    st.markdown("## ⚡ Quick Install Demo Data")
    _run_demo_installer_ui(API_URL)
    st.markdown("---")
    if st.button("← Back to Home"):
        st.session_state["_home_show_demo"] = False
        st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LIVE PLATFORM STATS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Live Platform Stats")
try:
    from utils.data_manager import get_available_tables, get_available_files
    tables = get_available_tables()
    files  = get_available_files()
    n_tables = len(tables)
    n_files  = len(files)
except Exception:
    n_tables = "—"
    n_files  = "—"

# Registered user count (best-effort — only works when logged in as admin or user with token)
n_users = "—"
try:
    import sqlite3
    from config.settings import settings as _s
    _conn = sqlite3.connect(_s.db_path)
    _cur  = _conn.cursor()
    _cur.execute("SELECT COUNT(*) FROM app_users")
    n_users = _cur.fetchone()[0]
    _conn.close()
except Exception:
    pass

# Demo install status
try:
    from utils.demo_installer import is_demo_already_installed
    _demo_done = is_demo_already_installed()
    demo_status = "✅ Installed" if _demo_done else "⏳ Pending"
except Exception:
    demo_status = "—"

smtp_configured = bool(settings.smtp_server)

stat_cols = st.columns(6)
stat_cols[0].metric("🗄️ SQL Tables",      n_tables,     help="Active tables in the SQLite database")
stat_cols[1].metric("📄 Uploaded Files",   n_files,      help="Documents indexed in the Knowledge Base")
stat_cols[2].metric("👥 Registered Users", n_users,      help="Total users in the platform database")
stat_cols[3].metric("⚡ Demo Data",         demo_status,  help="Whether demo seed data has been installed")
stat_cols[4].metric("📧 Email Mode",        "SMTP ✅" if smtp_configured else "Mock 📋",
                    help="Password reset email mode")
stat_cols[5].metric("🔒 Auth",             "JWT + BCrypt", help="Token-based auth with bcrypt password hashing")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT: MODULES + GUIDE CHAT
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 🚀 Intelligence Modules")

    # ── Module card helper ──────────────────────────────────────────────────
    def module_card(title, description, page, icon, demo_text=""):
        st.markdown(
            f"""<div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,75,75,0.18);
             border-radius: 14px; padding: 1.1rem 1.2rem; margin-bottom: 0.5rem;">
             <h4 style="margin: 0 0 0.4rem 0; color: #ff6b6b;">{title}</h4>
             <p style="margin: 0; color: #bbb; font-size: 0.88rem; line-height: 1.5;">{description}</p>
             </div>""",
            unsafe_allow_html=True
        )
        btn_col, demo_col = st.columns([3, 1])
        btn_col.page_link(page, label=f"Open {title.split(' ', 1)[-1]}", icon=icon)
        if demo_text:
            with demo_col.popover("👁 Preview"):
                st.markdown(demo_text)

    # ── Row 1 ───────────────────────────────────────────────────────────────
    r1a, r1b = st.columns(2)
    with r1a:
        module_card(
            "📁 Data Hub",
            "Upload CSV, PDF, SQL scripts, media & images. Supports Kaggle & GitHub connectors. "
            "Triggers automatic Graph Store and Knowledge Base rebuilds. "
            "Includes an **Interactive Graph Visualizer** with physics simulation and a **Graph Database Evaluation** panel.",
            "pages/1_📁_Data_Hub.py", "📂",
            demo_text="""
**Key Features:**
- 📤 CSV / PDF / SQL / media file uploads
- 🌍 External connectors: Kaggle & GitHub
- 🕸️ Interactive Neo4j graph explorer (zoom, drag, hover)
- 🔬 Graph DB Evaluation: health, performance, quality & retrieval
- 🎥 Image & audio ingestion for multimodal pipeline
"""
        )
    with r1b:
        module_card(
            "🧠 SQL RAG Assistant",
            "Ask natural-language questions against your SQL tables. Auto-generates and safely validates SQL queries with a security layer. "
            "Features auto-suggested questions whenever a table is selected.",
            "pages/2_🧠_SQL_RAG_Assistant.py", "💬",
            demo_text="""
**Key Features:**
- 💬 Natural language → SQL translation
- 🛡️ SQL injection prevention & security alerts
- 💡 Auto-generated contextual sample questions on table select
- 📊 ERD relationship diagrams (per-table)
- 📥 Export results to CSV
"""
        )

    # ── Row 2 ───────────────────────────────────────────────────────────────
    r2a, r2b = st.columns(2)
    with r2a:
        module_card(
            "🕸️ Graph RAG Assistant",
            "Explore fraud rings and entity relationships using Neo4j. Ask investigative questions in plain English — "
            "the system generates and runs Cypher queries. Auto-suggests graph investigation angles.",
            "pages/3_🕸️_Graph_RAG_Assistant.py", "🕸️",
            demo_text="""
**Key Features:**
- 🔍 Natural language → Cypher query generation
- 🧠 AI-suggested investigation angles
- 🌐 In-memory GDS graph projections
- 📋 Exportable PDF investigation reports
- 🏷️ Schema-aware with PK/FK context
"""
        )
    with r2b:
        module_card(
            "🎥 Multimodal RAG Assistant",
            "Chat with uploaded images, PDFs, videos, and audio files. "
            "The assistant reads documents and correlates physical evidence with transactional data.",
            "pages/4_🎥_Multimodal_RAG_Assistant.py", "🎥",
            demo_text="""
**Key Features:**
- 🖼️ Image analysis & OCR context
- 🎙️ Audio transcript extraction
- 📄 PDF & text document Q&A
- 🌐 Multilingual response (same language as query)
- 🔒 Hallucination guards in system prompt
"""
        )

    # ── Row 3 ───────────────────────────────────────────────────────────────
    r3a, r3b = st.columns(2)
    with r3a:
        module_card(
            "📈 Trends & Insights",
            "Discover fraud patterns through automated statistical analysis and visualization. "
            "AI-powered smart joins between tables for cross-dataset correlation.",
            "pages/5_📈_Trends_and_Insights.py", "📈",
            demo_text="""
**Key Features:**
- 📊 Single-table EDA with auto-visualizations
- 🔗 Smart multi-table join analysis (PK-aware)
- 📉 Time-series anomaly detection
- 📑 Exportable board-ready PDF reports
- 💡 AI-generated narrative summaries
"""
        )
    with r3b:
        module_card(
            "🔄 ML Workflow",
            "Train, evaluate, and compare fraud detection models. Full MLops pipeline: "
            "feature engineering, hyperparameter tuning, SHAP explainability, and model versioning.",
            "pages/6_🔄_ML_Workflow.py", "🧪",
            demo_text="""
**Key Features:**
- ⚙️ XGBoost / RandomForest with hyperparameter search
- 📐 SHAP feature importance visualization
- 🧪 Train/val/test split control
- 🗂️ Dataset & model versioning
- 🚀 1-click production scoring API
"""
        )

    # ── Row 4 ───────────────────────────────────────────────────────────────
    r4a, r4b = st.columns(2)
    with r4a:
        module_card(
            "🧬 LLM Fine-Tuning Forge",
            "Fine-tune open-source LLMs (Llama 3, Mistral) on your agency-specific fraud data. "
            "Compare fine-tuned vs. base model responses in real time.",
            "pages/9_🧠_LLM_Fine_Tuning.py", "🧬",
            demo_text="""
**Key Features:**
- 📚 Custom dataset curation from uploaded notes
- 🔥 LoRA / QLoRA fine-tuning on local hardware (MLX)
- 📊 Training loss curves & validation metrics
- 🆚 Side-by-side base vs. fine-tuned comparison
- 💾 Model checkpoint management
"""
        )
    with r4b:
        module_card(
            "🔌 API Integration Hub",
            "Explore the live REST API, test endpoints interactively, and integrate Sentinel "
            "with your existing SIEM, data warehouse, or case management system.",
            "pages/10_🔌_API_Interaction.py", "🔌",
            demo_text="""
**Key Features:**
- 🌐 Interactive OpenAPI / Swagger explorer
- 🔑 JWT-authenticated endpoint testing
- 📤 File ingestion & scoring API
- 📊 Model inference endpoints
- 📝 Auto-generated integration code snippets
"""
        )

    # ── Admin Console (conditional on permissions) ───────────────────────────
    perms = fetch_user_permissions()
    if "11_🛡️_Admin_Console" in perms:
        st.markdown("---")
        st.markdown("#### 🛡️ Platform Administration")
        module_card(
            "🛡️ Admin Console",
            "Full control over: **API Keys**, **User Management** (create / update email & role / reset password), "
            "**Role-Based Access Control**, **External Credentials** (Kaggle, GitHub), "
            "**Local LLM Manager** (Ollama pull/delete), **System Stats**, **📧 SMTP Configuration**, "
            "and **🚀 Onboarding Settings** (enable/disable Quick Install, re-run demo installer).",
            "pages/11_🛡️_Admin_Console.py", "🛡️",
            demo_text="""
**Admin Tabs:**
- 🔑 API Keys — OpenAI, Anthropic, Google, etc.
- 👥 User Management — create, update email/role, reset password, delete
- 🎭 Role Management — RBAC page-level permissions
- 🔐 External Credentials — Kaggle / GitHub tokens
- 🤖 Local LLMs — Ollama model pull / delete
- ⚙️ System Stats — uptime, docs, sessions
- 📧 SMTP Settings — configure real email delivery
- 🚀 Onboarding Settings — Quick Install toggle & re-run demo installer
"""
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Debug bar (shown only when user is logged in)
    if st.session_state.get("user"):
        h_perms = st.session_state.get("user_permissions")
        perm_display = str(len(h_perms)) if h_perms else "0"
        st.caption(f"🔧 Role: `{st.session_state.user.get('role', 'Guest')}` · Permissions: `{perm_display}`")

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN: AI Operator Chat + Quick-Start Guide
# ─────────────────────────────────────────────────────────────────────────────
with col_right:
    st.markdown("### 💬 Sentinel Operator")
    st.info("Your in-platform AI guide. Ask about investigative techniques, workflows, or how to use any feature.")

    # Quick-Start Guide accordion
    with st.expander("🚦 Quick-Start Guide", expanded=False):
        st.markdown("""
**Step 0 — First-Time Setup (new users)**
If this is your first time, click **⚡ Quick Install Demo Data** in the sidebar (visible when not logged in).
This will automatically create 3 demo users, execute 5 SQL seed scripts, and upload 2 fraud CSV datasets — all in one click.
After install, log in as `yanhuo68` / `yanhuo68ottawa` (admin).

---

**Step 1 — Load Data**
Go to **📁 Data Hub** → upload a CSV or run a SQL script. The graph and knowledge base rebuild automatically.

**Step 2 — Investigate with SQL**
Go to **🧠 SQL RAG Assistant** → select a table → ask natural-language questions.
Sample questions auto-appear when you pick a table.

**Step 3 — Explore the Fraud Network**
Go to **🕸️ Graph RAG Assistant** → ask *"Who are the key influencers?"* or click *"Suggest Investigation Angles"*.

**Step 4 — Visualize & Evaluate**
Back in **📁 Data Hub**, scroll to **Graph Visualization** and click **"▶ Run Full Evaluation"** to get a health score.

**Step 5 — Train a Model**
Go to **🔄 ML Workflow** → select features → train an XGBoost fraud classifier.

**Step 6 — Multimodal Evidence**
Go to **🎥 Multimodal RAG Assistant** → upload receipts, images, or audio → ask questions about physical evidence.

**Step 7 (Admin) — Platform Configuration**
Go to **🛡️ Admin Console** to:
- Add API keys (OpenAI, Anthropic, Google)
- Manage users and roles
- Configure SMTP for real email
- Disable the **⚡ Quick Install** button after setup (Onboarding Settings tab)
""")

    st.markdown("---")

    # Chat History
    if "guide_messages" not in st.session_state:
        st.session_state.guide_messages = []

    for msg in st.session_state.guide_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything about the Sentinel platform…"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.guide_messages.append({"role": "user", "content": prompt})

        with st.spinner("Consulting Sentinel protocols…"):
            guide = AppGuideAgent()
            chat_hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.guide_messages[:-1]]
            response = guide.ask(prompt, chat_history=chat_hist[-4:])

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.guide_messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑 Clear Chat", key="clear_guide"):
        st.session_state.guide_messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🗺️ Platform Architecture")
    st.markdown("""
| Layer | Technology |
|---|---|
| Frontend | Streamlit (hot-reload) |
| Backend API | FastAPI + Uvicorn |
| SQL Store | SQLite (via SQLAlchemy) |
| Graph Store | Neo4j (Bolt) |
| Vector KB | FAISS + HuggingFace Embeddings |
| LLM Engine | Ollama · OpenAI · Anthropic · Google |
| Auth | JWT · BCrypt · RBAC |
| Onboarding | One-click demo installer |
| Email | SMTP (configurable / mock) |
| Container | Docker Compose |
""")
