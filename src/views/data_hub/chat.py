import streamlit as st
import pandas as pd
from utils.data_manager import get_available_tables, get_available_files, load_data
from agents.pandas_agent import query_dataframe, generate_suggested_questions
from agents.text_agent import query_document, generate_document_questions

def clear_files():
    if "up_sel_files" in st.session_state:
        st.session_state.up_sel_files = []

def clear_tables():
    if "up_sel_tables" in st.session_state:
        st.session_state.up_sel_tables = []

def render_chat_section():
    st.markdown("---")
    st.header("💬 Chat with Uploaded Data")

    chat_df = None
    chat_text = None

    st.subheader("Select Data for Chat")
    col_src1, col_src2 = st.columns(2)
    with col_src1:
        avail_tables = get_available_tables()
        selected_tables = st.multiselect("SQL Tables:", avail_tables, key="up_sel_tables", on_change=clear_files)
    with col_src2:
        avail_files = get_available_files()
        selected_files = st.multiselect("Uploaded Files:", avail_files, key="up_sel_files", on_change=clear_tables)

    source_items = selected_tables + selected_files

    if st.button("🚀 Load & Generate Sample Questions"):
        if not source_items:
            st.warning("Please select at least one table or file.")
        elif selected_tables and selected_files:
            st.warning("⚠️ Please select either SQL Tables OR Uploaded Files, but not both at the same time.")
        else:
            with st.spinner("Loading data..."):
                sType = "SQL Tables" if selected_tables else "Uploaded File"
                data = load_data(sType, source_items)
                
                if data is not None:
                    if "upload_suggested_questions" in st.session_state: del st.session_state.upload_suggested_questions
                    if "upload_doc_suggestions" in st.session_state: del st.session_state.upload_doc_suggestions
                    if "upload_chat_history" in st.session_state: del st.session_state.upload_chat_history
                    if "upload_doc_history" in st.session_state: del st.session_state.upload_doc_history
                    
                    if isinstance(data, pd.DataFrame):
                        st.session_state.uploaded_df = data
                        st.session_state.uploaded_text = None
                        st.success(f"Loaded {len(data)} rows.")
                    elif isinstance(data, dict):
                        st.session_state.uploaded_text = data
                        st.session_state.uploaded_df = None
                        st.success(f"Loaded document: {data['filename']}")
                    else:
                        st.error("Unknown data format.")

    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        chat_df = st.session_state.uploaded_df
    elif 'uploaded_text' in st.session_state and st.session_state.uploaded_text is not None:
        chat_text = st.session_state.uploaded_text

    if chat_df is not None:
        if "upload_chat_history" not in st.session_state: st.session_state.upload_chat_history = []
        if "upload_suggested_questions" not in st.session_state: st.session_state.upload_suggested_questions = []

        if not st.session_state.upload_suggested_questions:
            with st.spinner("Generating sample questions..."):
                st.session_state.upload_suggested_questions = generate_suggested_questions(chat_df)

        for role, content in st.session_state.upload_chat_history:
            with st.chat_message(role):
                if role == "assistant" and isinstance(content, (pd.DataFrame, pd.Series)):
                    st.dataframe(content)
                else:
                    st.write(content)

        if st.session_state.upload_suggested_questions:
            st.write("Need inspiration?")
            u_cols = st.columns(len(st.session_state.upload_suggested_questions))
            for i, q in enumerate(st.session_state.upload_suggested_questions):
                if u_cols[i].button(q, key=f"up_sugg_{i}"):
                    st.session_state.upload_chat_history.append(("user", q))
                    st.session_state.upload_processing_prompt = q
                    st.rerun()

        u_prompt = st.chat_input("Ask a question about this data...")
        if u_prompt:
            st.session_state.upload_chat_history.append(("user", u_prompt))
            st.session_state.upload_processing_prompt = u_prompt
            st.rerun()
            
        if "upload_processing_prompt" in st.session_state and st.session_state.upload_processing_prompt:
            prompt_to_run = st.session_state.upload_processing_prompt
            del st.session_state.upload_processing_prompt
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    resp = query_dataframe(chat_df, prompt_to_run)
                    if isinstance(resp, (pd.DataFrame, pd.Series)):
                        st.dataframe(resp)
                    else:
                        st.write(resp)
                    st.session_state.upload_chat_history.append(("assistant", resp))

    elif chat_text is not None:
        if "upload_doc_history" not in st.session_state: st.session_state.upload_doc_history = []
        if "upload_doc_suggestions" not in st.session_state: st.session_state.upload_doc_suggestions = []

        doc_content = chat_text["content"]
        
        if not st.session_state.upload_doc_suggestions:
            with st.spinner("Analyzing document..."):
                st.session_state.upload_doc_suggestions = generate_document_questions(doc_content)
        
        for role, content in st.session_state.upload_doc_history:
            with st.chat_message(role):
                st.write(content)
                
        if st.session_state.upload_doc_suggestions:
            st.write("Suggested/Sample Questions:")
            d_cols = st.columns(len(st.session_state.upload_doc_suggestions))
            for i, q in enumerate(st.session_state.upload_doc_suggestions):
                if d_cols[i].button(q, key=f"up_doc_sugg_{i}"):
                    st.session_state.upload_doc_history.append(("user", q))
                    st.session_state.upload_doc_prompt = q
                    st.rerun()

        d_prompt = st.chat_input("Ask about the document...")
        if d_prompt:
            st.session_state.upload_doc_history.append(("user", d_prompt))
            st.session_state.upload_doc_prompt = d_prompt
            st.rerun()
            
        if "upload_doc_prompt" in st.session_state and st.session_state.upload_doc_prompt:
            final_d_prompt = st.session_state.upload_doc_prompt
            del st.session_state.upload_doc_prompt
            
            with st.chat_message("assistant"):
                with st.spinner("Reading..."):
                    ans = query_document(doc_content, final_d_prompt)
                    st.write(ans)
                    st.session_state.upload_doc_history.append(("assistant", ans))

    else:
        st.info("Select data and click 'Load' to start chatting.")
