import streamlit as st
import os
from utils.data_manager import get_available_tables, SYSTEM_TABLES

def render_manage_section():
    st.markdown("---")
    st.header("📂 Manage Uploaded Files & Tables")
    st.caption("View, inspect, and delete data assets loaded into the platform.")

    fm_tab_tables, fm_tab_docs, fm_tab_media, fm_tab_pics = st.tabs(
        ["🗄️ SQL Tables", "📄 Documents & CSV", "🎥 Media Files", "🖼️ Images"]
    )

    with fm_tab_tables:
        st.subheader("Loaded SQL Tables")
        st.caption("Only user-created tables are shown. System tables (app_users, app_roles, api_keys) are hidden and protected.")
        try:
            fm_tables = get_available_tables()   # already filtered by SYSTEM_TABLES
            if not fm_tables:
                st.info("No user tables found. Upload a CSV or run a SQL script.")
            else:
                for tbl in fm_tables:
                    # Extra safety: skip any system table that slipped through
                    if tbl in SYSTEM_TABLES:
                        continue
                    t_col1, t_col2, t_col3 = st.columns([3, 2, 1])
                    t_col1.markdown(f"**🗄️ {tbl}**")
                    # Quick row + column count
                    try:
                        import sqlite3 as _sqlite3
                        from config.settings import settings as _settings
                        con = _sqlite3.connect(_settings.db_path)
                        row_count = con.execute(f"SELECT COUNT(*) FROM '{tbl}'").fetchone()[0]
                        col_count = len(con.execute(f"PRAGMA table_info('{tbl}')").fetchall())
                        con.close()
                        t_col2.caption(f"{row_count:,} rows · {col_count} cols")
                    except Exception:
                        t_col2.caption("—")
                    if t_col3.button("🗑 Drop", key=f"drop_tbl_{tbl}", help=f"Permanently drop table '{tbl}'"):
                        # Final guard: never drop system tables
                        if tbl in SYSTEM_TABLES:
                            st.error(f"⛔ Table '{tbl}' is a protected system table and cannot be dropped.")
                        else:
                            try:
                                import sqlite3 as _sqlite3
                                from config.settings import settings as _settings
                                con = _sqlite3.connect(_settings.db_path)
                                con.execute(f"DROP TABLE IF EXISTS '{tbl}'")
                                con.commit()
                                con.close()
                                st.success(f"Table '{tbl}' dropped.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to drop table: {e}")
                    st.divider()
        except Exception as e:
            st.error(f"Could not list tables: {e}")

    with fm_tab_docs:
        st.subheader("Uploaded Documents & CSV Files")
        upload_dir = "data/uploads"
        try:
            if not os.path.exists(upload_dir):
                st.info("No uploads directory found.")
            else:
                doc_files = sorted(os.listdir(upload_dir))
                doc_files = [f for f in doc_files if not f.startswith(".")]
                if not doc_files:
                    st.info("No uploaded files found.")
                else:
                    for fname in doc_files:
                        fpath = os.path.join(upload_dir, fname)
                        fsize = os.path.getsize(fpath)
                        fsize_str = f"{fsize/1024:.1f} KB" if fsize < 1024*1024 else f"{fsize/1024/1024:.2f} MB"
                        dc1, dc2, dc3 = st.columns([4, 2, 1])
                        dc1.markdown(f"📄 **{fname}**")
                        dc2.caption(fsize_str)
                        if dc3.button("🗑", key=f"del_doc_{fname}", help=f"Delete '{fname}'"):
                            try:
                                os.remove(fpath)
                                st.success(f"Deleted '{fname}'.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not delete: {e}")
        except Exception as e:
            st.error(f"Error listing uploads: {e}")

    with fm_tab_media:
        st.subheader("Uploaded Media Files (Audio/Video)")
        media_dir = "data/mediauploads"
        try:
            if not os.path.exists(media_dir) or not os.listdir(media_dir):
                st.info("No media files uploaded yet.")
            else:
                for fname in sorted(os.listdir(media_dir)):
                    if fname.startswith("."):
                        continue
                    fpath = os.path.join(media_dir, fname)
                    fsize = os.path.getsize(fpath)
                    fsize_str = f"{fsize/1024/1024:.2f} MB"
                    mc1, mc2, mc3 = st.columns([4, 2, 1])
                    mc1.markdown(f"🎥 **{fname}**")
                    mc2.caption(fsize_str)
                    if mc3.button("🗑", key=f"del_media_{fname}", help=f"Delete '{fname}'"):
                        try:
                            os.remove(fpath)
                            st.success(f"Deleted '{fname}'.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not delete: {e}")
        except Exception as e:
            st.error(f"Error listing media: {e}")

    with fm_tab_pics:
        st.subheader("Uploaded Images")
        pic_dir = "data/pictureuploads"
        try:
            if not os.path.exists(pic_dir) or not os.listdir(pic_dir):
                st.info("No images uploaded yet.")
            else:
                pic_list = [f for f in sorted(os.listdir(pic_dir)) if not f.startswith(".")]
                pic_cols = st.columns(4)
                for i, fname in enumerate(pic_list):
                    fpath = os.path.join(pic_dir, fname)
                    with pic_cols[i % 4]:
                        st.image(fpath, caption=fname, use_container_width=True)
                        if st.button("🗑 Delete", key=f"del_pic_{fname}"):
                            try:
                                os.remove(fpath)
                                st.success(f"Deleted '{fname}'.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not delete: {e}")
        except Exception as e:
            st.error(f"Error listing images: {e}")
