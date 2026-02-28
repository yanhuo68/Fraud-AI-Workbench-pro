import streamlit as st
import pandas as pd
import os
from pathlib import Path
from rag_sql.sql_utils import run_sql_query
from rag_sql.file_loader import extract_text_from_file
from agents.llm_router import init_llm

# Tables that belong to the application itself and must never be shown or modified
# by user-facing features (SQL RAG, Trends, ML Workflow, File Management Panel, etc.)
SYSTEM_TABLES = frozenset({
    "app_users",
    "app_roles",
    "api_keys",
})

def get_available_tables():
    """Fetch user-created table names from SQLite DB, excluding system tables."""
    try:
        df, _ = run_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        if df.empty:
            return []
        return [t for t in df["name"].tolist() if t not in SYSTEM_TABLES]
    except Exception:
        return []

def get_available_files():
    """Scan upload directory for files."""
    upload_dir = os.path.join("data", "uploads")
    if not os.path.exists(upload_dir):
        return []
    return [f for f in os.listdir(upload_dir) if not f.startswith('.')]

def get_table_schema(table_name):
    """Get columns for a table to help LLM join them, including Primary Key info."""
    try:
        df, _ = run_sql_query(f"PRAGMA table_info({table_name})")
        # limit to name, type, and pk flag
        cols = []
        for _, r in df.iterrows():
            pk_str = " (PK)" if r['pk'] else ""
            cols.append(f"{r['name']} {r['type']}{pk_str}")
        
        return f"Table {table_name}: " + ", ".join(cols)
    except:
        return f"Table {table_name}: (schema unknown)"

def generate_join_query(tables):
    """Ask LLM to write a JOIN query for the selected tables."""
    schema_context = []
    for t in tables:
        schema_context.append(get_table_schema(t))
    
    schema_str = "\n".join(schema_context)
    
    prompt = (
        "You are a SQL Expert. Write a valid SQLite query to JOIN these tables using likely foreign keys.\n"
        f"Selected Tables: {tables}\n"
        f"Schemas (PK indicates Primary Key):\n{schema_str}\n\n"
        "Rules:\n"
        "1. Return ONLY the raw SQL query. No markdown, no comments, no extra text.\n"
        "2. Join ALL selected tables. Use LEFT JOIN or INNER JOIN as appropriate (prefer INNER if keys exist).\n"
        "3. **STRICT COLUMN NAMES**: Use ONLY column names provided in the schemas above. Do NOT assume an 'id' column exists if it is not listed (e.g., if a table has 'location_id', use that, NOT 'id').\n"
        "4. LOOK FOR INTERMEDIARY TABLES: If Table A and Table B have no direct common column, check if Table C links them (e.g. Devices -> Transactions -> Locations).\n"
        "5. SELECT ALL COLUMNS: Use `SELECT *` or `SELECT T1.*, T2.*` to fetch all data from all joined tables.\n"
        "6. Limit result to 5000 rows.\n"
    )
    
    try:
        llm = init_llm("openai:gpt-4o-mini")
        response = llm.invoke(prompt)
        sql = response.content.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        st.error(f"LLM Join Generation Failed: {e}")
        return None

def deduplicate_columns(df):
    """Renames duplicate columns (e.g., user_id, user_id_1)."""
    if df is None: return None
    new_cols = []
    seen = {}
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols
    return df

def convert_datetime_columns(df):
    """Attempt to parse common datetime columns."""
    if df is None: return None
    for col in df.columns:
        # Check if object or string-like
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
            try:
                # Heuristic: Check column name
                if any(x in col.lower() for x in ['date', 'time', 'created', 'seen', 'timestamp']):
                     # Use coerce to force conversion of valid formats, NaT for invalid
                     df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
    return df

def load_data(source_type, source_items):
    """Load data into DataFrame or Text Wrapper based on selection."""
    try:
        if source_type == "SQL Tables":
            if not source_items: return None
            
            # Single Table
            if len(source_items) == 1:
                sql = f'SELECT * FROM "{source_items[0]}" LIMIT 5000'
                st.session_state.last_run_sql = sql
                df, _ = run_sql_query(sql)
                return convert_datetime_columns(deduplicate_columns(df))
            
            # Multi Table (Smart Join)
            else:
                st.info(f"🤖 Generating Smart Join for: {', '.join(source_items)}...")
                sql = generate_join_query(source_items)
                if sql:
                    # Persist SQL for display
                    st.session_state.last_run_sql = sql
                    df, _ = run_sql_query(sql)
                    return convert_datetime_columns(deduplicate_columns(df))
                return None
                
        elif source_type == "Uploaded File":
            # Files usually single select
            if not source_items: return None
            fname = source_items[0]
            path = Path("data/uploads") / fname
            
            # Clear SQL state if loading file
            if 'last_run_sql' in st.session_state:
                del st.session_state.last_run_sql
                
            if fname.endswith('.csv'):
                df = pd.read_csv(path)
                return convert_datetime_columns(deduplicate_columns(df))
            elif fname.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(path)
                return convert_datetime_columns(deduplicate_columns(df))
            elif fname.endswith(('.pdf', '.txt', '.md')):
                content, _ = extract_text_from_file(str(path))
                return {"type": "text", "content": content, "filename": fname}
                
        return None
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None
