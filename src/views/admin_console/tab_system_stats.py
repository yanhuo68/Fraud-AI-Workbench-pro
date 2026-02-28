import streamlit as st
import pandas as pd
import requests

def render_system_stats_tab(API_URL, headers):
    st.header("⚙️ System Stats")
    st.caption("Live snapshot of storage, datasets, and system health.")

    import shutil as _shutil
    from pathlib import Path as _Path
    import json as _json_sys

    if st.button("🔄 Refresh Stats", type="primary"):
        st.session_state["_stats_refresh"] = True

    # ── Disk usage ─────────────────────────────────────────────────────────────
    st.subheader("💾 Storage")
    _total, _used, _free = _shutil.disk_usage("/")
    _used_gb  = _used  / (1024 ** 3)
    _free_gb  = _free  / (1024 ** 3)
    _total_gb = _total / (1024 ** 3)
    _used_pct = _used / _total

    _sc1, _sc2, _sc3 = st.columns(3)
    _sc1.metric("Total Disk",  f"{_total_gb:.1f} GB")
    _sc2.metric("Used",        f"{_used_gb:.1f} GB",  delta=f"{_used_pct:.0%} used",  delta_color="off")
    _sc3.metric("Free",        f"{_free_gb:.1f} GB",  delta="Available",              delta_color="off")
    st.progress(_used_pct, text=f"{_used_pct:.0%} disk used")

    st.markdown("---")

    # ── Data directory file counts ──────────────────────────────────────────────
    st.subheader("📂 Data Directory Overview")
    _data_dirs = {
        "data/uploads":           "Uploaded Files",
        "data/ml":                "ML Artefacts",
        "data/llm":               "LLM Datasets",
        "data/generated":         "Generated Reports",
        "data/graph":             "Graph Data",
    }
    _dir_rows = []
    for _dp, _label in _data_dirs.items():
        _p = _Path(_dp)
        if _p.exists():
            _files = list(_p.rglob("*"))
            _n_files = sum(1 for _f in _files if _f.is_file())
            _size_bytes = sum(_f.stat().st_size for _f in _files if _f.is_file())
            _size_mb = _size_bytes / (1024 ** 2)
        else:
            _n_files, _size_mb = 0, 0.0
        _dir_rows.append({"Directory": _label, "Path": _dp, "Files": _n_files, "Size (MB)": f"{_size_mb:.2f}"})
    _dir_df = pd.DataFrame(_dir_rows)
    st.dataframe(_dir_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── ML & LLM versioned assets ───────────────────────────────────────────────
    st.subheader("🧠 ML & LLM Assets")
    _ml_c1, _ml_c2, _ml_c3, _ml_c4 = st.columns(4)

    # Scoring history rows
    _hist_path = _Path("data/ml/scoring_history.csv")
    _n_scored = 0
    if _hist_path.exists():
        try:
            _n_scored = sum(1 for _ in open(_hist_path)) - 1  # subtract header
        except Exception:
            _n_scored = 0
    _ml_c1.metric("Scored Transactions", f"{max(_n_scored, 0):,}")

    # LLM dataset sample counts
    _llm_datasets_dir = _Path("data/llm/datasets")
    _n_ds = len(list(_llm_datasets_dir.iterdir())) if _llm_datasets_dir.exists() else 0
    _ml_c2.metric("LLM Datasets", _n_ds)

    # Total LLM samples
    _total_samples = 0
    if _llm_datasets_dir.exists():
        for _ds_dir in _llm_datasets_dir.iterdir():
            _samples_file = _ds_dir / "samples.jsonl"
            if _samples_file.exists():
                try:
                    _total_samples += sum(1 for _ in open(_samples_file))
                except Exception:
                    pass
    _ml_c3.metric("LLM Training Samples", _total_samples)

    # Registered model count
    _models_dir = _Path("data/llm/models")
    _metadata_file = _models_dir / "metadata.json"
    _n_models = 0
    if _metadata_file.exists():
        try:
            with open(_metadata_file) as _mf:
                _meta = _json_sys.load(_mf)
            _n_models = len(_meta.get("models", []))
        except Exception:
            pass
    _ml_c4.metric("Registered LLM Models", _n_models)

    st.markdown("---")

    # ── Backend health check ────────────────────────────────────────────────────
    st.subheader("🏥 Backend Health")
    _h_c1, _h_c2 = st.columns(2)
    try:
        import time as _time
        _t0 = _time.time()
        _hrsp = requests.get(f"{API_URL}/health", headers=headers, timeout=5)
        _lat = _time.time() - _t0
        if _hrsp.status_code == 200:
            _h_c1.success(f"✅ FastAPI Backend — HTTP {_hrsp.status_code} ({_lat:.2f}s)")
            _hdata = _hrsp.json()
            if isinstance(_hdata, dict):
                _h_c2.json(_hdata)
        else:
            _h_c1.warning(f"⚠️ FastAPI responded HTTP {_hrsp.status_code}")
    except Exception as _he:
        _h_c1.error(f"❌ FastAPI unreachable: {_he}")

    # ── Onboarding / Quick Install Settings ─────────────────────────────────────
    st.markdown("---")
    st.subheader("🚀 Onboarding Settings")
    st.info(
        "Control the **Quick Install Demo Data** button visibility on the Authentication wall "
        "and sidebar. Disable it once your environment is set up to prevent unauthorized data installs."
    )

    try:
        from utils.demo_installer import (
            is_demo_button_enabled, is_demo_already_installed, set_demo_button_enabled,
            install_demo_data, DEMO_CATALOGUE, _read_settings
        )
        _ob_settings = _read_settings()
        _ob_enabled   = _ob_settings.get("quick_demo_install_enabled", True)
        _ob_installed  = _ob_settings.get("quick_demo_installed", False)
        _ob_ts         = _ob_settings.get("demo_install_timestamp")

        _ob_c1, _ob_c2, _ob_c3 = st.columns(3)
        _ob_c1.metric("Button Visible", "✅ Enabled" if _ob_enabled else "🔒 Disabled")
        _ob_c2.metric("Demo Installed", "✅ Yes" if _ob_installed else "⬜ Not yet")
        _ob_c3.metric("Installed At", _ob_ts[:19].replace("T"," ") if _ob_ts else "—")

        st.markdown("#### Toggle Button Visibility")
        _t1, _t2 = st.columns(2)
        if _ob_enabled:
            if _t1.button("🔒 Disable Quick Install Button", type="secondary", use_container_width=True):
                set_demo_button_enabled(False)
                st.success("✅ Quick Install button is now **disabled** on the auth wall and sidebar.")
                st.rerun()
        else:
            if _t1.button("✅ Enable Quick Install Button", type="primary", use_container_width=True):
                set_demo_button_enabled(True)
                st.success("✅ Quick Install button is now **enabled**.")
                st.rerun()

        with st.expander("📦 Demo Data Contents", expanded=False):
            for section, items in DEMO_CATALOGUE.items():
                st.markdown(f"**{section}**")
                for item in items:
                    st.markdown(f"- {item}")

        st.markdown("#### Re-run Demo Installer (Admin-initiated)")
        st.warning("⚠️ This will attempt to re-run the installer. Existing users/data will be skipped (no duplicates).")
        if st.button("🔄 Re-run Demo Installer Now", use_container_width=True):
            _log_area = st.empty()
            _pbar     = st.progress(0)
            _lines    = []

            def _admin_cb(step, total, message, ok):
                _pbar.progress(step / total)
                _lines.append(message)
                _log_area.markdown("\n\n".join(_lines))

            with st.spinner("Running demo installer…"):
                _res = install_demo_data(API_URL, progress_callback=_admin_cb)

            if _res["success"]:
                st.success("🎉 Demo installer completed successfully!")
            else:
                st.warning("Some steps had issues — check the log above.")

    except Exception as _ob_e:
        st.error(f"Could not load onboarding settings: {_ob_e}")
