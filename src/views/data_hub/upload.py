import streamlit as st
import pandas as pd
import requests
import os
from views.data_hub.utils import get_headers, auto_rebuild, API_URL

def render_upload_tab():
    headers = get_headers()
    st.header("📤 Upload Files")
    col_upload, col_demo = st.columns(2)

    with col_upload:
        uploaded_file = st.file_uploader("Upload file", type=["csv", "pdf", "txt", "json", "md"])

    with col_demo:
        st.write("💡 **Quick Start: Demo Data**")
        demo_dir = "data/raw"
        try:
            demo_files = [f for f in os.listdir(demo_dir) if f.endswith(".csv")]
            selected_demo = st.selectbox("Select Demo Dataset:", ["-- None --"] + demo_files)
            if st.button("🚀 Load Demo CSV"):
                if selected_demo != "-- None --":
                    file_path = os.path.join(demo_dir, selected_demo)
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    files = {"file": (selected_demo, file_bytes, "text/csv")}
                    with st.spinner(f"Ingesting {selected_demo}..."):
                        resp = requests.post(f"{API_URL}/ingest/file", headers=headers, files=files)
                    
                    if resp.status_code == 200:
                        st.success(f"Successfully loaded '{selected_demo}'!")
                        if auto_rebuild():
                            st.balloons()
                            st.info("Friend message: Data uploaded and both Graph Store & Knowledge Base have been rebuilt successfully! You are ready to investigate.")
                    else:
                        st.error(f"Failed to load demo: {resp.text}")
        except Exception as e:
            st.error(f"Could not list demo files: {e}")

    if uploaded_file:
        # Show file info + preview
        file_type = uploaded_file.name.split('.')[-1].lower()
        file_bytes = uploaded_file.getvalue()
        file_size_kb = len(file_bytes) / 1024
        df = None

        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("📄 File", uploaded_file.name)
        info_col2.metric("📦 Size", f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.2f} MB")
        info_col3.metric("🗂 Type", file_type.upper())

        if file_type == "csv":
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(), use_container_width=True)
                st.caption(f"Preview: {len(df)} rows × {len(df.columns)} columns")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        else:
            st.info(f"File '{uploaded_file.name}' selected for ingestion (preview not available for {file_type})")

        if st.button("⬆️ Upload to Backend", type="primary"):
            upload_progress = st.progress(0, text="Preparing upload...")
            uploaded_file.seek(0)
            files = {
                "file": (uploaded_file.name, file_bytes, f"application/{file_type}")
            }
            upload_progress.progress(25, text="Sending to backend...")

            try:
                resp = requests.post(
                    f"{API_URL}/ingest/file",
                    headers=headers,
                    files=files
                )
                upload_progress.progress(75, text="Processing on server...")
            except Exception as e:
                upload_progress.empty()
                st.error(f"Connection error: {e}")
                resp = None

            if resp is not None:
                upload_progress.progress(100, text="Done!")
                if resp.status_code != 200:
                    st.error(f"Upload failed: {resp.text}")
                else:
                    data = resp.json()
                    st.success(f"✅ File processed: {data.get('message', 'OK')}")
                    if auto_rebuild():
                        st.balloons()
                        st.info("Data uploaded and both Graph Store & Knowledge Base rebuilt successfully!")

                    # Update frontend state if it was a table
                    if data.get("processed_as") == "table" and df is not None:
                        table = data.get("table_name")
                        if table:
                            st.session_state.uploaded_tables[table] = f"docs/schema_{table}.md"
                            st.session_state.uploaded_df = df

    # --- SQL Scripts (Moved to Upload Tab) ---
    st.markdown("---")
    st.header("🛠️ Run SQL Script")

    col_sql_up, col_sql_demo = st.columns(2)

    with col_sql_up:
        sql_files = st.file_uploader("Upload .sql file(s)", type=["sql"], accept_multiple_files=True)

    with col_sql_demo:
        st.write("💡 **Quick Start: Demo SQL**")
        sql_demo_dir = "data/raw/sql"
        try:
            demo_sqls = [f for f in os.listdir(sql_demo_dir) if f.endswith(".sql")]
            selected_sql = st.selectbox("Select Demo SQL Script:", ["-- None --"] + demo_sqls)
            if st.button("⚡ Execute Demo SQL"):
                if selected_sql != "-- None --":
                    file_path = os.path.join(sql_demo_dir, selected_sql)
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    files = {"file": (selected_sql, file_bytes, "application/sql")}
                    with st.spinner(f"Executing {selected_sql}..."):
                        resp = requests.post(f"{API_URL}/ingest/execute-sql", headers=headers, files=files)
                    
                    if resp.status_code == 200:
                        st.success(f"Successfully executed '{selected_sql}'!")
                        if auto_rebuild():
                            st.balloons()
                            st.info("Friend message: SQL script executed and both Graph Store & Knowledge Base have been rebuilt successfully! Data is ready for analysis.")
                    else:
                        st.error(f"Failed to execute SQL: {resp.text}")
        except Exception as e:
            st.error(f"Could not list demo SQL files: {e}")

    if sql_files:
        # If single file usage in loop, handle list
        count_success = 0
        total_files = len(sql_files)
        
        if st.button("Execute SQL Scripts"):
            progress_bar = st.progress(0)
            
            for i, sql_file in enumerate(sql_files):
                try:
                    # Reset pointer just in case
                    sql_file.seek(0)
                    
                    files = {
                        "file": (sql_file.name, sql_file.getvalue(), "application/sql")
                    }
                    
                    resp = requests.post(f"{API_URL}/ingest/execute-sql", headers=headers, files=files)
                        
                    if resp.status_code == 200:
                        st.toast(f"Executed: {sql_file.name}", icon="✅")
                        count_success += 1
                    else:
                        st.error(f"Failed {sql_file.name}: {resp.text}")
                except Exception as e:
                    st.error(f"Error processing {sql_file.name}: {e}")
                
                # Update progress
                progress_bar.progress((i + 1) / total_files)

            if count_success == total_files:
                st.success(f"Successfully executed all {total_files} scripts!")
                if auto_rebuild():
                    st.balloons()
                    st.info("Friend message: All SQL scripts executed and both Graph Store & Knowledge Base have been rebuilt successfully! Database is up to date.")
            elif count_success > 0:
                 st.warning(f"Executed {count_success} out of {total_files} scripts.")
                 if auto_rebuild():
                     st.info("Rebuild complete for partial success.")

    # --- Media Uploads ---
    st.markdown("---")
    st.header("🎥 Media Uploads (Audio/Video)")
    st.info("Upload media files for future Multimodal RAG analysis. These files are saved to `data/mediauploads`.")

    media_files = st.file_uploader(
        "Upload Audio or Video files", 
        type=["mp3", "wav", "mp4", "mov", "avi", "mkv"], 
        accept_multiple_files=True
    )

    if media_files:
        saved_count = 0
        media_dir = "data/mediauploads"
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            
        for mfile in media_files:
            path = os.path.join(media_dir, mfile.name)
            with open(path, "wb") as f:
                f.write(mfile.getbuffer())
            saved_count += 1
            
        if saved_count > 0:
            st.success(f"Saved {saved_count} media files successfully.")

    # --- Picture Uploads ---
    st.markdown("---")
    st.header("🖼️ Picture Uploads")
    st.info("Upload images for analysis. These files are saved to `data/pictureuploads`.")

    pic_files = st.file_uploader(
        "Upload Images", 
        type=["png", "jpg", "jpeg", "webp"], 
        accept_multiple_files=True,
        key="pic_uploader"
    )

    if pic_files:
        saved_pic_count = 0
        pic_dir = "data/pictureuploads"
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)
            
        for pfile in pic_files:
            path = os.path.join(pic_dir, pfile.name)
            with open(path, "wb") as f:
                f.write(pfile.getbuffer())
            saved_pic_count += 1
            
        if saved_pic_count > 0:
            st.success(f"Saved {saved_pic_count} images successfully.")
