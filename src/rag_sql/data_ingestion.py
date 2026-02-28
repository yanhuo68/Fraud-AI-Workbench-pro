# rag_sql/data_ingestion.py

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
import sqlite3
from datetime import datetime
import re
import logging

from rag_sql.pkfk_detector import detect_primary_key, detect_foreign_keys
from config.settings import settings

logger = logging.getLogger(__name__)


def sanitize_table_name(filename: str) -> str:
    """
    Convert filename to a safe SQLite table name.
    Examples:
        "Fraud Data.csv" -> "fraud_data"
        "2024-Jan-Transactions.csv" -> "t2024_jan_transactions"
    """
    name = filename.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    if name and name[0].isdigit():
        name = "t_" + name
    return name


def write_schema_markdown(df: pd.DataFrame, table_name: str, docs_dir: Path = None):
    """Write basic schema markdown without PK/FK information."""
    if docs_dir is None:
        docs_dir = settings.docs_dir_obj
    
    docs_dir.mkdir(parents=True, exist_ok=True)
    schema_path = docs_dir / f"schema_{table_name}.md"

    lines = []
    lines.append(f"# Schema for `{table_name}`\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n\n")
    lines.append("| Column | Pandas Type | SQL Type | Null Count | Sample |\n")
    lines.append("|--------|-------------|----------|------------|--------|\n")

    for col in df.columns:
        dtype = str(df[col].dtype)

        if "int" in dtype:
            sql_type = "INTEGER"
        elif "float" in dtype:
            sql_type = "REAL"
        else:
            sql_type = "TEXT"

        nulls = df[col].isna().sum()
        sample = str(df[col].dropna().iloc[0]) if df[col].dropna().any() else ""

        lines.append(f"| {col} | {dtype} | {sql_type} | {nulls} | {sample} |\n")

    lines.append("\n")
    lines.append("### Notes\n")
    lines.append(f"- Table name: `{table_name}`\n")
    lines.append("- Generated automatically from uploaded file.\n")

    schema_path.write_text("".join(lines), encoding="utf-8")
    logger.info(f"Schema written to {schema_path}")
    return schema_path


def write_schema_markdown_with_pkfk(
    df: pd.DataFrame,
    table_name: str,
    primary_key: Optional[str],
    foreign_keys: List[tuple],
    docs_dir: Path = None,
):
    """Write schema markdown with PK/FK information."""
    if docs_dir is None:
        docs_dir = settings.docs_dir_obj
    
    docs_dir.mkdir(parents=True, exist_ok=True)
    schema_path = docs_dir / f"schema_{table_name}.md"

    lines = []
    lines.append(f"# Schema for `{table_name}`\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n\n")

    # Primary Key
    lines.append("## Primary Key\n")
    lines.append(f"- `{primary_key}`\n\n" if primary_key else "- None detected\n\n")

    # Foreign Keys
    lines.append("## Foreign Keys\n")
    if foreign_keys:
        for fk in foreign_keys:
            table_A, colA, table_B, pkB = fk
            lines.append(f"- `{colA}` → `{table_B}.{pkB}`\n")
    else:
        lines.append("- None detected\n")
    lines.append("\n")

    # Columns table
    lines.append("## Columns\n")
    lines.append("| Column | Pandas Type | Nulls | Sample |\n")
    lines.append("|--------|-------------|--------|----------|\n")
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isna().sum()
        sample = str(df[col].dropna().iloc[0]) if df[col].dropna().any() else ""
        lines.append(f"| {col} | {dtype} | {nulls} | {sample} |\n")

    schema_path.write_text("".join(lines), encoding="utf-8")
    logger.info(f"Schema with PK/FK written to {schema_path}")
    return schema_path


def ingest_uploaded_csv_dynamic(
    df: pd.DataFrame,
    filename: str,
    table_dataframes: Optional[Dict[str, pd.DataFrame]] = None,
    table_pkfk: Optional[Dict[str, dict]] = None,
    db_path: Optional[Path] = None,
    docs_dir: Optional[Path] = None,
    rebuild_kb: bool = True,
) -> Tuple[str, Dict[str, pd.DataFrame], Dict[str, dict]]:
    """
    Ingest a CSV DataFrame into SQLite and generate schema documentation.
    
    Args:
        df: DataFrame to ingest
        filename: Original filename (used for table naming)
        table_dataframes: Existing table dataframes dict (default: empty dict)
        table_pkfk: Existing PK/FK metadata dict (default: empty dict)
        db_path: Database path (default: from settings)
        docs_dir: Documentation directory (default: from settings)
        rebuild_kb: Whether to rebuild knowledge base (default: True)
    
    Returns:
        Tuple of (table_name, updated_table_dataframes, updated_table_pkfk)
    """
    # Initialize defaults
    if table_dataframes is None:
        table_dataframes = {}
    if table_pkfk is None:
        table_pkfk = {}
    if db_path is None:
        db_path = settings.db_path_obj
    if docs_dir is None:
        docs_dir = settings.docs_dir_obj
    
    # Create copies to avoid mutating input
    table_dataframes = table_dataframes.copy()
    table_pkfk = table_pkfk.copy()
    
    table_name = sanitize_table_name(filename)
    logger.info(f"Ingesting table: {table_name} from {filename}")
    
    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save table to database
    conn = sqlite3.connect(str(db_path))
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logger.info(f"Table {table_name} saved to database with {len(df)} rows")
    except Exception as e:
        logger.error(f"Failed to save table {table_name}: {e}")
        raise
    finally:
        conn.close()

    # Detect PK
    pk = detect_primary_key(df)
    logger.info(f"Detected primary key for {table_name}: {pk}")

    # Update table dataframes
    table_dataframes[table_name] = df

    # Detect FK across all tables
    primary_keys = {t: detect_primary_key(df_t) for t, df_t in table_dataframes.items()}
    foreign_keys = detect_foreign_keys(table_dataframes, primary_keys)
    logger.info(f"Detected {len(foreign_keys)} foreign key relationships")

    # Update PK/FK mapping
    table_pkfk[table_name] = {
        "primary_key": pk,
        "foreign_keys": [fk for fk in foreign_keys if fk[0] == table_name]
    }

    # Write schema file including PK/FK
    schema_path = write_schema_markdown_with_pkfk(
        df, table_name, pk, table_pkfk[table_name]["foreign_keys"], docs_dir
    )

    # Consolidate all schemas into central reference file
    try:
        from rag_sql.schema_consolidator import consolidate_schemas_to_reference
        consolidate_schemas_to_reference(table_dataframes, table_pkfk, docs_dir)
        logger.info("Central schema reference updated")
    except Exception as e:
        logger.warning(f"Failed to update central schema reference: {e}")

    # Rebuild KB so schema is included
    if rebuild_kb:
        try:
            from rag_sql.build_kb_index import build_vectorstore
            kb_dir = settings.kb_dir_obj
            build_vectorstore(docs_dir=docs_dir, out_dir=kb_dir)
            logger.info("Knowledge base rebuilt successfully")
        except Exception as e:
            logger.warning(f"Failed to rebuild knowledge base: {e}")

    return table_name, table_dataframes, table_pkfk


