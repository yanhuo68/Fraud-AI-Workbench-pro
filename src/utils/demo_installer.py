from __future__ import annotations
"""
demo_installer.py
─────────────────
Utilities for the "Quick Install Demo Data" onboarding feature.

Responsibilities
────────────────
1. Read / write  data/config/app_settings.json        → toggle enabled/disabled state
2. install_demo_data(api_url)                          → run the full one-shot setup:
   a) Create 3 demo users via /auth/register  (uses NULL email to avoid duplicate clash)
   b) Login as admin to obtain a Bearer token for authenticated endpoints
   c) Execute the 5 SQL seed scripts via /ingest/execute-sql  (requires admin token)
   d) Upload the two demo CSV files via /ingest/file           (requires any user token)
   e) Mark installed + disable the button in app_settings.json
"""
"""Utility script to quickly download and ingest fake demo data"""

import streamlit as st
import json
import requests
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
_BASE_DIR      = Path(__file__).parent.parent
_SETTINGS_FILE = _BASE_DIR / "data" / "config" / "app_settings.json"
_SQL_DIR       = _BASE_DIR / "data" / "raw" / "sql"
_CSV_DEMO_FILES = [
    _BASE_DIR / "data" / "raw" / "Fraud Detection Dataset.csv",
    _BASE_DIR / "data" / "raw" / "Fraud Detection Dataset_Mock_Data.csv",
]
_SQL_SCRIPTS = [
    _SQL_DIR / "step_1_relational_db_creatse.sql",
    _SQL_DIR / "step_2_customer_insert.sql",
    _SQL_DIR / "step_3_catalog_insert.sql",
    _SQL_DIR / "step_4_orders_insert.sql",
    _SQL_DIR / "step_5_orderdetail_insert.sql",
]

# ─── Demo Users ───────────────────────────────────────────────────────────────
# Each user gets a distinct placeholder email so the uniqueness check never clashes.
# Users can update their email from the Admin Console after first login.
DEMO_USERS = [
    {"username": "stephane@qubec",   "password": "stephane2026",  "email": "stephane@demo.local", "role": "guest"},
    {"username": "david@ontario",    "password": "david2026",      "email": "david@demo.local",    "role": "data_scientist"},
    {"username": "yanhuo68",         "password": "yanhuo68ottawa", "email": "yanhuo68@demo.local", "role": "admin"},
]

# Admin credentials used to authenticate after user creation (SQL/CSV need auth)
_ADMIN_USERNAME = "yanhuo68"
_ADMIN_PASSWORD = "yanhuo68ottawa"


# ─── Settings helpers ─────────────────────────────────────────────────────────
def _ensure_settings_file():
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not _SETTINGS_FILE.exists():
        _write_settings({
            "quick_demo_install_enabled": True,
            "quick_demo_installed": False,
            "demo_install_timestamp": None,
        })


def _read_settings() -> dict:
    _ensure_settings_file()
    try:
        with open(_SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read app_settings.json: {e}")
        return {"quick_demo_install_enabled": True, "quick_demo_installed": False, "demo_install_timestamp": None}


def _write_settings(data: dict):
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def is_demo_button_enabled() -> bool:
    return _read_settings().get("quick_demo_install_enabled", True)


def is_demo_already_installed() -> bool:
    return _read_settings().get("quick_demo_installed", False)


def set_demo_button_enabled(enabled: bool):
    s = _read_settings()
    s["quick_demo_install_enabled"] = enabled
    _write_settings(s)


def _mark_installed():
    s = _read_settings()
    s["quick_demo_installed"] = True
    s["quick_demo_install_enabled"] = False
    s["demo_install_timestamp"] = datetime.now(timezone.utc).isoformat()
    _write_settings(s)


# ─── Core installer ───────────────────────────────────────────────────────────
def install_demo_data(api_url: str, progress_callback=None) -> dict:
    """
    Run the full demo data installation.

    Flow
    ────
    1.  Create demo users  (unauthenticated endpoint)
    2.  Login as admin     (get Bearer token for authenticated endpoints)
    3.  Execute SQL seed   (requires admin Bearer)
    4.  Upload CSVs        (requires any user Bearer)
    5.  Mark installed     (auto-disables the Quick Install button)

    Parameters
    ----------
    api_url : str
        Base URL of the FastAPI backend, e.g. "http://fastapi:8000".
    progress_callback : callable(step: int, total: int, message: str, ok: bool) | None

    Returns
    -------
    dict  { success: bool, steps: list[dict] }
    """
    results   = []
    # total: user creation + 1 auth step + SQL scripts + CSV files
    total_steps = len(DEMO_USERS) + 1 + len(_SQL_SCRIPTS) + len(_CSV_DEMO_FILES)
    step = 0

    def _report(msg: str, ok: bool = True):
        nonlocal step
        step += 1
        results.append({"step": step, "message": msg, "ok": ok})
        logger.info(f"[DemoInstall] step={step}/{total_steps} ok={ok}: {msg}")
        if progress_callback:
            try:
                progress_callback(step, total_steps, msg, ok)
            except Exception:
                pass

    # ── 1. Create demo users (no auth required) ───────────────────────────────
    for user in DEMO_USERS:
        try:
            resp = requests.post(
                f"{api_url}/auth/register",
                json={
                    "username": user["username"],
                    "password": user["password"],
                    "email":    user["email"],   # None → JSON null → DB NULL
                    "role":     user["role"],
                },
                timeout=15,
            )
            if resp.status_code == 200:
                _report(f"✅ User created: **{user['username']}** (role: {user['role']})", ok=True)
            elif resp.status_code == 400:
                detail = resp.json().get("detail", "")
                if "already" in detail.lower() or "exists" in detail.lower():
                    _report(f"⏭️ User already exists: **{user['username']}** — skipped", ok=True)
                else:
                    _report(f"⚠️ User **{user['username']}**: {detail}", ok=False)
            else:
                try:
                    detail = resp.json().get("detail", resp.text[:200])
                except Exception:
                    detail = resp.text[:200]
                _report(f"❌ Failed to create **{user['username']}**: HTTP {resp.status_code} — {detail}", ok=False)
        except Exception as e:
            _report(f"❌ Error creating **{user['username']}**: {e}", ok=False)

    # ── 2. Login as admin to get Bearer token ─────────────────────────────────
    bearer_token = None
    try:
        auth_resp = requests.post(
            f"{api_url}/auth/token",
            data={"username": _ADMIN_USERNAME, "password": _ADMIN_PASSWORD},
            timeout=15,
        )
        if auth_resp.status_code == 200:
            bearer_token = auth_resp.json().get("access_token")
            _report("✅ Authenticated as admin — ready for data import", ok=True)
        else:
            try:
                detail = auth_resp.json().get("detail", auth_resp.text[:200])
            except Exception:
                detail = auth_resp.text[:200]
            _report(
                f"❌ Could not authenticate as `{_ADMIN_USERNAME}` (HTTP {auth_resp.status_code}: {detail}). "
                "SQL and CSV import will be skipped.",
                ok=False
            )
    except Exception as e:
        _report(f"❌ Authentication request failed: {e}. SQL and CSV import will be skipped.", ok=False)

    auth_headers = {"Authorization": f"Bearer {bearer_token}"} if bearer_token else {}

    # ── 3. Execute SQL seed scripts (requires admin token) ────────────────────
    for sql_path in _SQL_SCRIPTS:
        if not sql_path.exists():
            _report(f"⚠️ SQL file not found: `{sql_path.name}` — skipped", ok=False)
            continue
        if not bearer_token:
            _report(f"⏭️ SQL `{sql_path.name}` skipped — no auth token available", ok=False)
            continue
        try:
            with open(sql_path, "rb") as f:
                files = {"file": (sql_path.name, f, "text/plain")}
                resp = requests.post(
                    f"{api_url}/ingest/execute-sql",
                    files=files,
                    headers=auth_headers,
                    timeout=60,
                )
            if resp.status_code == 200:
                _report(f"✅ SQL executed: `{sql_path.name}`", ok=True)
            else:
                try:
                    detail = resp.json().get("detail", resp.text[:200])
                except Exception:
                    detail = resp.text[:200]
                _report(f"⚠️ SQL `{sql_path.name}`: HTTP {resp.status_code} — {detail}", ok=False)
        except Exception as e:
            _report(f"❌ Error running `{sql_path.name}`: {e}", ok=False)

    # ── 4. Upload demo CSV files (requires user token) ────────────────────────
    for csv_path in _CSV_DEMO_FILES:
        if not csv_path.exists():
            _report(f"⚠️ CSV file not found: `{csv_path.name}` — skipped", ok=False)
            continue
        if not bearer_token:
            _report(f"⏭️ CSV `{csv_path.name}` skipped — no auth token available", ok=False)
            continue
        try:
            with open(csv_path, "rb") as f:
                files = {"file": (csv_path.name, f, "text/csv")}
                resp = requests.post(
                    f"{api_url}/ingest/file",
                    files=files,
                    headers=auth_headers,
                    timeout=120,
                )
            if resp.status_code in (200, 201):
                _report(f"✅ CSV uploaded: `{csv_path.name}`", ok=True)
            else:
                try:
                    detail = resp.json().get("detail", resp.text[:200])
                except Exception:
                    detail = resp.text[:200]
                _report(f"⚠️ CSV `{csv_path.name}`: HTTP {resp.status_code} — {detail}", ok=False)
        except Exception as e:
            _report(f"❌ Error uploading `{csv_path.name}`: {e}", ok=False)

    # ── 5. Mark as installed (auto-disables button) ───────────────────────────
    # Only mark installed if the admin user exists (i.e., creation or skip succeeded)
    admin_ok = any(
        r.get("ok") and "yanhuo68" in r.get("message", "")
        for r in results
    )
    if admin_ok or bearer_token:  # bearer_token means auth worked → users exist
        try:
            _mark_installed()
            results.append({
                "step": "final",
                "message": "✅ Demo installation complete — Quick Install button auto-disabled for security.",
                "ok": True,
            })
        except Exception as e:
            results.append({"step": "final", "message": f"⚠️ Could not save installed state: {e}", "ok": False})
    else:
        results.append({
            "step": "final",
            "message": "⚠️ Admin user creation failed — installer NOT marked as complete. You can retry.",
            "ok": False,
        })

    overall_ok = all(r.get("ok", True) for r in results)
    return {"success": overall_ok, "steps": results}


# ─── Demo content catalogue ───────────────────────────────────────────────────
DEMO_CATALOGUE = {
    "👥 Users Created": [
        "`stephane@qubec` — role: **guest**         — password: `stephane2026`  — email: stephane@demo.local",
        "`david@ontario`  — role: **data_scientist** — password: `david2026`     — email: david@demo.local",
        "`yanhuo68`       — role: **admin**          — password: `yanhuo68ottawa`— email: yanhuo68@demo.local",
    ],
    "🗄️ Relational Database (SQL)": [
        "`step_1` — creates schema: Customer, Catalog, Orders, OrderDetail tables",
        "`step_2` — inserts seed customer records",
        "`step_3` — inserts product catalog data",
        "`step_4` — inserts fraud investigation order data",
        "`step_5` — inserts order line-item detail",
    ],
    "📊 CSV Files (SQL DB + Vector Store + Graph)": [
        "`Fraud Detection Dataset.csv` — primary fraud transaction records",
        "`Fraud Detection Dataset_Mock_Data.csv` — synthetic fraud mock data for ML training",
    ],
}
