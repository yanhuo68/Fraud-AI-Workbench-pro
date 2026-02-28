import streamlit as st
from views.api_interaction.helpers import make_request, _ep

def render_ingest_tab(api_base_url):
    col_a, col_b = st.columns(2)

    with col_a:
        _ep("POST", "/ingest/file", "auth")
        st.caption("Upload a file (CSV → SQL + Vector + Graph, PDF/images → Graph KB).")
        with st.expander("📌 Supported types & behaviour"):
            st.markdown("""
| Extension | SQL Table | Graph Store | Knowledge Base |
|---|---|---|---|
| CSV | ✅ auto-create table | ✅ doc node | ✅ rebuild |
| PDF | — | ✅ text extracted | ✅ rebuild |
| PNG/JPG | — | ✅ image node | ✅ rebuild |
| MP3/WAV | — | ✅ transcript | ✅ rebuild |
| MP4 | — | ✅ frames + transcript | ✅ rebuild |
""")
        up_file = st.file_uploader(
            "Select file", type=["csv", "pdf", "png", "jpg", "jpeg", "mp3", "mp4", "sql"],
            key="api_ingest_file"
        )
        if st.button("⬆️ Ingest File", use_container_width=True, key="ingest_file_btn"):
            if up_file:
                make_request("POST", "/ingest/file", api_base_url, files={"file": (up_file.name, up_file.getvalue(), up_file.type)})
            else:
                st.warning("Upload a file first.")

    with col_b:
        _ep("POST", "/ingest/execute-sql", "admin")
        st.caption("Execute a SQL script (`.sql` file) against the SQLite database. Admin only.")
        with st.expander("📌 How it works"):
            st.markdown("""
- Parses `CREATE TABLE` statements and drops existing tables before re-creating
- Executes the full script via `conn.executescript()`
- Stores the SQL as a document in the Graph Store
- Syncs schema changes to the graph
""")
        sql_file = st.file_uploader("Select .sql file", type=["sql"], key="api_ingest_sql")
        if st.button("▶️ Execute SQL Script", use_container_width=True, key="exec_sql_btn"):
            if sql_file:
                make_request("POST", "/ingest/execute-sql", api_base_url,
                             files={"file": (sql_file.name, sql_file.getvalue(), "text/plain")})
            else:
                st.warning("Upload a .sql file first.")
