import streamlit as st
from pathlib import Path
import logging

from rag_sql.build_kb_index import build_vectorstore
from rag_sql.erd_generator import build_mermaid_erd
from config.settings import settings

logger = logging.getLogger(__name__)


def init_state():
    """Initialize Streamlit session state variables."""
    if "uploaded_df" not in st.session_state:
        st.session_state.uploaded_df = None
    if "uploaded_tables" not in st.session_state:
        st.session_state.uploaded_tables = {}
    if "table_dataframes" not in st.session_state:
        st.session_state.table_dataframes = {}
    if "table_pkfk" not in st.session_state:
        st.session_state.table_pkfk = {}
    if "best_df" not in st.session_state:
        st.session_state.best_df = None
    if "last_rag_result" not in st.session_state:
        st.session_state.last_rag_result = None
    # Authentication state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = None
    if "user_permissions" not in st.session_state:
        st.session_state.user_permissions = None


def build_schema_text_from_tables() -> str:
    """Wrapped for backward compatibility."""
    from utils.schema_utils import build_schema_text_from_tables as build_schema
    return build_schema()


def rebuild_kb_index_with_erd():
    """
    Rebuild KB (vector store) including ERD diagram.
    Uses session state to access table information.
    """
    docs_dir = settings.docs_dir_obj
    kb_dir = settings.kb_dir_obj
    
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Generate ERD if we have tables with PK/FK info
    if st.session_state.table_dataframes and st.session_state.table_pkfk:
        try:
            erd_text = build_mermaid_erd(
                st.session_state.table_dataframes,
                st.session_state.table_pkfk,
            )
            erd_path = docs_dir / "erd_diagram.md"
            erd_path.write_text(erd_text, encoding="utf-8")
            logger.info(f"ERD diagram generated: {erd_path}")
        except Exception as e:
            logger.error(f"Failed to generate ERD: {e}")

    # Rebuild vector store
    try:
        build_vectorstore(docs_dir=docs_dir, out_dir=kb_dir)
        logger.info("Knowledge base rebuilt successfully")
    except Exception as e:
        logger.error(f"Failed to rebuild knowledge base: {e}")
        raise

