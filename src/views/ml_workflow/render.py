import streamlit as st
from utils.dashboard_state import init_state
from components.sidebar import render_global_sidebar, enforce_page_access

from views.ml_workflow.tab_build import render_build_tab
from views.ml_workflow.tab_train import render_train_tab
from views.ml_workflow.tab_score import render_score_tab
from views.ml_workflow.tab_tune import render_tune_tab
from views.ml_workflow.tab_deploy import render_deploy_tab
from views.ml_workflow.tab_monitor import render_monitor_tab

def render_ml_workflow():
    init_state()
    enforce_page_access("6_🔄_ML_Workflow")
    render_global_sidebar()

    user = st.session_state.get("user")
    is_admin = user and user.get("role") == "admin"
    is_ds = user and user.get("role") == "data_scientist"
    can_control = is_admin or is_ds

    st.title("🔄 End-to-End ML Workflow")
    st.info("A unified workflow to Build Datasets, Auto-Train Models, and Score Live Data.")

    tab_build, tab_train, tab_score, tab_tune, tab_deploy, tab_monitor = st.tabs([
        "🧪 1. Build Dataset", 
        "🤖 2. Train Models", 
        "⚡ 3. Live Scoring",
        "🔧 4. Fine-Tuning (Data)",
        "🚀 5. Deploy Model",
        "📊 6. Monitor Model"
    ])

    with tab_build:
        render_build_tab(can_control)
    
    with tab_train:
        render_train_tab(can_control)
        
    with tab_score:
        render_score_tab()
        
    with tab_tune:
        render_tune_tab(can_control)
        
    with tab_deploy:
        render_deploy_tab(can_control)
        
    with tab_monitor:
        render_monitor_tab()
