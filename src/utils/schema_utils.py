import sqlite3
import pandas as pd
import logging
from pathlib import Path
from config.settings import settings
from utils.data_manager import SYSTEM_TABLES

logger = logging.getLogger(__name__)

def build_schema_text_from_tables() -> str:
    """
    Generate schema context for the LLM by introspecting the SQLite database.
    This ensures accurate, up-to-date schema even for tables created via SQL scripts.
    Filters out system tables and explicitly lists Foreign Key relationships.
    """
    schema_parts = []
    
    try:
        if not settings.db_path_obj.exists():
            return "No database found."

        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cursor.fetchall() if r[0] not in SYSTEM_TABLES]
            
            if not tables:
                return "Database is empty (no user tables found)."
            
            schema_parts.append(f"Database contains {len(tables)} tables: {', '.join(tables)}\n")
            schema_parts.append("CRITICAL INSTRUCTION: ONLY use these exact table names. DO NOT hallucinate other tables (like 'orders' or 'products') if they are not listed here.\n")
            
            for table in tables:
                schema_parts.append(f"--- Table: {table} ---")
                
                # 2. Get CREATE TABLE statement
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
                create_sql = cursor.fetchone()
                if create_sql and create_sql[0]:
                    schema_parts.append(create_sql[0] + ";")

                # 3. Get explicit Foreign Keys to prevent LLM hallucinating joins
                fks = cursor.execute(f"PRAGMA foreign_key_list('{table}')").fetchall()
                if fks:
                    schema_parts.append("\nExplicit Relationships (Foreign Keys):")
                    for fk in fks:
                        # fk index: id, seq, table(ref_table), from, to, on_update, on_delete, match
                        ref_table, from_col, to_col = fk[2], fk[3], fk[4]
                        schema_parts.append(f"- Column '{from_col}' references '{ref_table}({to_col})'")
                else:
                    schema_parts.append("\nExplicit Relationships: NONE. Do NOT JOIN this table with other tables unless you have a perfectly matching semantic column.")

                # 4. Get Sample Data (3 rows) to help LLM understand values
                try:
                    df_sample = pd.read_sql_query(f"SELECT * FROM \"{table}\" LIMIT 3", conn)
                    if not df_sample.empty:
                        schema_parts.append(f"\nSample Data for {table}:")
                        schema_parts.append(df_sample.to_markdown(index=False))
                except Exception as e:
                    logger.warning(f"Could not fetch sample data for {table}: {e}")
                
                schema_parts.append("\n==================================\n")

    except Exception as e:
        logger.error(f"Error building schema text: {e}")
        return f"Error retrieving schema: {e}"

    return "\n".join(schema_parts)
