import streamlit as st
from utils.dashboard_state import init_state
from components.sidebar import render_global_sidebar, enforce_page_access

from views.trends.data_selection import render_data_selection
from views.trends.structured_analysis import render_structured_analysis
from views.trends.unstructured_analysis import render_unstructured_analysis

def render_trends_and_insights():
    init_state()
    enforce_page_access("5_📈_Trends_and_Insights")
    render_global_sidebar()

    # Initialize Page-Specific Session State
    if "analysis_df" not in st.session_state:
        st.session_state.analysis_df = None
    if "analysis_text" not in st.session_state:
        st.session_state.analysis_text = None
    if "analysis_source" not in st.session_state:
        st.session_state.analysis_source = None

    st.title("📈 Trends & Insights")

    # 1. UI: Data Selection
    source_type, selected_source = render_data_selection()

    # 2. DISPLAY LOGIC 
    if "analysis_df" in st.session_state and st.session_state.analysis_df is not None:
        render_structured_analysis(st.session_state.analysis_df)

    elif "analysis_text" in st.session_state and st.session_state.analysis_text is not None:
        render_unstructured_analysis(st.session_state.analysis_text)
        
    else:
        if not selected_source:
            st.info("Please select a data source above to begin.")
