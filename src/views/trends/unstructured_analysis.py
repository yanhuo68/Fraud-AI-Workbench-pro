import streamlit as st
import datetime
from pathlib import Path
from agents.llm_router import init_llm
from agents.text_agent import query_document, generate_document_questions
from utils.pdf_gen import create_trends_report

def render_unstructured_analysis(doc_data: dict):
    content = doc_data["content"]
    fname = doc_data["filename"]
    
    st.markdown(f"**Current Document:** `{fname}` ({len(content)} characters)")
    
    with st.expander("📄 View Text Content", expanded=True):
        st.text_area("Content Preview", content[:5000], height=300)
    
    st.subheader("🧠 Document Analysis")
    
    task = st.selectbox("Select Analysis Task:", [
        "Summarize Key Themes",
        "Extract Risk Indicators",
        "Identify Key Entities (People, Orgs, Locations)",
        "Suggest Follow-up Investigation"
    ])
    
    if st.button(f"Run Analysis: {task}"):
        with st.spinner(f"AI is analyzing '{fname}'..."):
            try:
                llm_id = st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini")
                llm = init_llm(llm_id)
                prompt = (
                    f"You are an expert Intelligence Analyst. Analyze the following document text.\n"
                    f"Task: {task}\n\n"
                    f"Document Name: {fname}\n"
                    f"Document Content (truncated if too long):\n"
                    f"{content[:15000]}\n\n" 
                    f"Provide a concise, professional report."
                )
                response = llm.invoke(prompt)
                
                st.session_state.last_doc_analysis = response.content
                st.markdown("### 📝 AI Report")
                st.markdown(response.content)
            except Exception as e:
                st.error(f"Analysis Failed: {e}")

    # --- REPORT GENERATION (UNSTRUCTURED) ---
    st.markdown("---")
    st.subheader("📄 Export Report")
    
    report_opts_col1_doc, report_opts_col2_doc = st.columns([3, 1])
    with report_opts_col1_doc:
        custom_out_dir_doc = st.text_input("Save Report To (Folder Path):", value="data/generated", key="doc_out_dir")

    if st.button("Generate PDF Report", key="btn_doc_pdf"):
        try:
            sections = []
            
            sections.append({
                "title": "Document Context",
                "content": f"Filename: {fname}\nSize: {len(content)} chars\n\nPreview:\n{content[:1000]}..."
            })
            
            if "last_doc_analysis" in st.session_state:
                sections.append({
                    "title": f"AI Analysis: {task}", 
                    "content": st.session_state.last_doc_analysis
                })
            else:
                sections.append({
                    "title": "Note",
                    "content": "No AI analysis was run before generating this report."
                })
            
            out_dir = Path(custom_out_dir_doc)
            out_dir.mkdir(parents=True, exist_ok=True)
            
            report_filename = f"{fname}_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            report_path = str(out_dir / report_filename)
            
            create_trends_report(
                source_name=f"Document: {fname}",
                sections=sections,
                output_path=report_path
            )
            
            st.success(f"Report saved to: `{report_path}`")
            
            with open(report_path, "rb") as f:
                st.download_button("Download PDF", f, file_name=report_filename)
                
        except Exception as e:
            st.error(f"Report Failed: {e}")


    # --- CHAT WITH DOCUMENT ---
    st.markdown("---")
    st.subheader("💬 Chat with Document")
    
    if "doc_chat_history" not in st.session_state:
        st.session_state.doc_chat_history = []
        
    if "doc_suggested_questions" not in st.session_state:
        st.session_state.doc_suggested_questions = []
        
    if content and not st.session_state.doc_suggested_questions:
        with st.spinner("Generating sample questions..."):
            st.session_state.doc_suggested_questions = generate_document_questions(content)
            
    for role, msg in st.session_state.doc_chat_history:
        with st.chat_message(role):
            st.write(msg)
            
    if st.session_state.doc_suggested_questions:
        st.write("Need inspiration?")
        doc_cols = st.columns(len(st.session_state.doc_suggested_questions))
        for i, q in enumerate(st.session_state.doc_suggested_questions):
            if doc_cols[i].button(q, key=f"doc_sugg_{i}"):
                st.session_state.doc_chat_history.append(("user", q))
                st.session_state.doc_processing_prompt = q
                st.rerun()

    doc_prompt = st.chat_input("Ask about this document...")
    
    final_doc_prompt = None
    if doc_prompt:
        final_doc_prompt = doc_prompt
    elif "doc_processing_prompt" in st.session_state and st.session_state.doc_processing_prompt:
        final_doc_prompt = st.session_state.doc_processing_prompt
        del st.session_state.doc_processing_prompt
        
    if final_doc_prompt:
        if not doc_prompt: pass 
        else:
            st.session_state.doc_chat_history.append(("user", final_doc_prompt))
            with st.chat_message("user"):
                st.write(final_doc_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Reading..."):
                ans = query_document(content, final_doc_prompt)
                st.write(ans)
                st.session_state.doc_chat_history.append(("assistant", ans))

    if st.session_state.get("doc_chat_history"):
        if st.button("🗑 Clear Chat History", key="clear_doc_chat"):
            st.session_state.doc_chat_history = []
            st.rerun()
