import streamlit as st
from components.sidebar import render_global_sidebar, enforce_page_access
from utils.dashboard_state import init_state

# Import all extracted components
from views.data_hub.admin_controls import render_admin_controls
from views.data_hub.upload import render_upload_tab
from views.data_hub.external import render_external_tab
from views.data_hub.manage import render_manage_section
from views.data_hub.chat import render_chat_section
from views.data_hub.graph import render_graph_section

def render_data_hub():
    """Main entry point for the Data Hub page rendering logic."""
    # Initialize session state & sidebar routing
    init_state()
    enforce_page_access("1_📁_Data_Hub")
    render_global_sidebar()

    # Admin Sidebar Functions
    render_admin_controls()

    st.title("📁 Data Hub (via FastAPI backend)")

    # Data ingestion tabs
    tab_upload, tab_external = st.tabs(["📤 Upload Files", "🌍 External Data (Kaggle/GitHub)"])
    
    with tab_upload:
        render_upload_tab()
        
    with tab_external:
        render_external_tab()

    # Asset management, analysis, and visualization
    render_manage_section()
    render_chat_section()
    render_graph_section()
