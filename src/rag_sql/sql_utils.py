# rag_sql/sql_utils.py

"""
Utilities for executing SQL against the SQLite database used by SQL RAG.
Includes validation and security measures.
"""

from pathlib import Path
from typing import Tuple, List, Any, Union
import sqlite3
import pandas as pd
import logging
# removed signal import to avoid main thread enforcement in Streamlit

from rag_sql.sql_validator import validate_and_sanitize, SQLValidationError

logger = logging.getLogger(__name__)


class QueryTimeoutError(Exception):
    """Raised when SQL query exceeds timeout."""
    pass


def run_sql_query(
    query: str,
    db_path: Union[str, Path] = None,
    validate: bool = True,
    timeout_seconds: int = 30,
    max_rows: int = 10000,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Execute a SQL query with validation and safety measures.
    
    Args:
        query: SQL query string to execute
        db_path: Path to SQLite database (defaults to settings.DB_PATH)
        validate: Whether to validate SQL before execution (default: True)
        timeout_seconds: Query timeout in seconds (default: 30) - Currently best-effort via SQLite param
        max_rows: Maximum rows to return (default: 10000)
    
    Returns:
        Tuple of (DataFrame of results, List of column names)
    
    Raises:
        SQLValidationError: If query fails validation
        QueryTimeoutError: If query exceeds timeout
        sqlite3.Error: If SQL execution fails
    """
    # Use centralized DB path if not provided
    if db_path is None:
        from config.settings import settings
        db_path = settings.db_path
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    # Validate and sanitize SQL
    if validate:
        try:
            query, metadata = validate_and_sanitize(query, max_rows=max_rows)
            # logger.info(f"SQL validation passed: {metadata}")
        except SQLValidationError as e:
            logger.error(f"SQL validation failed: {e}")
            raise
    
    # Execute query
    # Note: sqlite3 connects fast, so we set timeout in connect but that is for locking, not query execution duration.
    # Python sqlite3 doesn't have an easy query execution timeout without signal or interrupt.
    # We will proceed without strict timeout for now to ensure Streamlit compatibility.
    conn = sqlite3.connect(str(db_path), timeout=timeout_seconds)
    
    try:
        logger.info(f"Executing SQL query: {query[:200]}...")
        df = pd.read_sql_query(query, conn)
        logger.info(f"Query returned {len(df)} rows, {len(df.columns)} columns")
        
    except sqlite3.Error as e:
        logger.error(f"SQL execution error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during query execution: {e}")
        raise
    finally:
        conn.close()
    
    cols = list(df.columns)
    return df, cols

