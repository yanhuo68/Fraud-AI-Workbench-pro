import streamlit as st
from utils.dashboard_state import init_state
from components.sidebar import render_global_sidebar, enforce_page_access

from views.multimodal_rag.tab_av import render_av_tab
from views.multimodal_rag.tab_picture import render_picture_tab
from views.multimodal_rag.tab_text import render_text_tab
from views.multimodal_rag.tab_web import render_web_tab
from views.multimodal_rag.tab_aware import render_aware_tab

def render_multimodal_rag():
    init_state()
    enforce_page_access("4_🎥_Multimodal_RAG_Assistant")

    st.title("🎥 Multimodal RAG Assistant")
    st.caption("Upload files in **Data Hub** tab. Here you can transcribe and analyze them.")

    render_global_sidebar()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎥 Audio/Video RAG", "🖼️ Picture RAG", "📝 Text RAG", "🌐 Web RAG", "🧠 Aware RAG"])

    with tab1:
        render_av_tab()
    with tab2:
        render_picture_tab()
    with tab3:
        render_text_tab()
    with tab4:
        render_web_tab()
    with tab5:
        render_aware_tab()
