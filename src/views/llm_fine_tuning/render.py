import streamlit as st
import os
from utils.dashboard_state import init_state
from components.sidebar import render_global_sidebar, enforce_page_access
from utils.version_manager import DatasetManager, ModelManager

from views.llm_fine_tuning.tab_collect import render_collect_tab
from views.llm_fine_tuning.tab_review import render_review_tab
from views.llm_fine_tuning.tab_train import render_train_tab
from views.llm_fine_tuning.tab_test import render_test_tab

def render_llm_fine_tuning():
    init_state()
    enforce_page_access("9_🧠_LLM_Fine_Tuning")
    render_global_sidebar()
    
    is_admin = st.session_state.get("user") and st.session_state.user.get("role") == "admin"
    
    st.title("🧠 LLM Fine-Tuning Lab")
    st.info("Fine-tune language models to improve fraud analysis reasoning using your expert feedback.")
    
    # Initialize managers globally for the tab
    dataset_mgr = DatasetManager()
    model_mgr = ModelManager()

    tab_collect, tab_review, tab_train, tab_test = st.tabs([
        "📝 1. Data Collection", 
        "📊 2. Dataset Review", 
        "🔧 3. Fine-Tuning",
        "🧪 4. Model Testing"
    ])
    
    with tab_collect:
        render_collect_tab(is_admin, dataset_mgr)
        
    with tab_review:
        render_review_tab(dataset_mgr)
        
    with tab_train:
        render_train_tab(is_admin, dataset_mgr, model_mgr)
        
    with tab_test:
        render_test_tab(dataset_mgr, model_mgr)
