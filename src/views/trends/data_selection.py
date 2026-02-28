import streamlit as st
import pandas as pd
from utils.data_manager import get_available_tables, get_available_files, load_data

def clear_state():
    """Clear analysis state when switching modes."""
    st.session_state.analysis_df = None
    st.session_state.analysis_text = None
    st.session_state.analysis_source = None
    if 'last_run_sql' in st.session_state: del st.session_state.last_run_sql
    if 'geo_summary' in st.session_state: del st.session_state.geo_summary
    if 'last_location_analysis' in st.session_state: del st.session_state.last_location_analysis
    if 'suggested_questions' in st.session_state: del st.session_state.suggested_questions
    if 'doc_chat_history' in st.session_state: del st.session_state.doc_chat_history
    if 'doc_suggested_questions' in st.session_state: del st.session_state.doc_suggested_questions
    if 'trend_insights' in st.session_state: del st.session_state.trend_insights
    if 'trend_active' in st.session_state: del st.session_state.trend_active
    if 'trend_df' in st.session_state: del st.session_state.trend_df

def render_data_selection():
    st.subheader("1. Select Data Source")

    col1, col2 = st.columns(2)
    with col1:
        source_type = st.radio(
            "Source Type:", 
            ["SQL Tables", "Uploaded File"], 
            horizontal=True,
            on_change=clear_state
        )

    selected_source = []

    if source_type == "SQL Tables":
        available_tables = get_available_tables()
        selected_source = st.multiselect("Select Tables (for automatic JOIN):", available_tables)
        
        if st.button("🚀 Smart Join & Load Data"):
            with st.spinner("Analyzing schema and joining tables..."):
                data = load_data(source_type, selected_source)
                if data is not None:
                    st.session_state.analysis_source = f"{source_type}: {', '.join(selected_source)}"
                    if 'suggested_questions' in st.session_state: del st.session_state.suggested_questions
                    if 'doc_suggested_questions' in st.session_state: del st.session_state.doc_suggested_questions
                    
                    if isinstance(data, pd.DataFrame):
                        st.session_state.analysis_df = data
                        st.session_state.analysis_text = None 
                        st.rerun() 
                    elif isinstance(data, dict) and data.get("type") == "text":
                        st.session_state.analysis_text = data
                        st.session_state.analysis_df = None 
                        st.rerun()

        if 'last_run_sql' in st.session_state:
            with st.expander("🔍 View Generated SQL Query", expanded=False):
                st.code(st.session_state.last_run_sql, language="sql")

    elif source_type == "Uploaded File":
        files = get_available_files()
        if files:
            f = st.selectbox("Choose File:", files)
            if f: selected_source = [f]
        else:
            st.info("No files found in data/uploads/.")

        if selected_source:
            if st.button("Load File Data"):
                with st.spinner("Processing..."):
                    data = load_data(source_type, selected_source)
                    if data is not None:
                        st.session_state.analysis_source = f"{source_type}: {', '.join(selected_source)}"
                        if 'suggested_questions' in st.session_state: del st.session_state.suggested_questions
                        if 'doc_suggested_questions' in st.session_state: del st.session_state.doc_suggested_questions
                        
                        if isinstance(data, pd.DataFrame):
                            st.session_state.analysis_df = data
                            st.session_state.analysis_text = None 
                            st.rerun() 
                        elif isinstance(data, dict) and data.get("type") == "text":
                            st.session_state.analysis_text = data
                            st.session_state.analysis_df = None 
                            st.rerun()

    return source_type, selected_source
