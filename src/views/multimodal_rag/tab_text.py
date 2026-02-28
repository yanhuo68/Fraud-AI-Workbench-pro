import streamlit as st
import os
from pathlib import Path
from agents.multimodal_agent import (
    analyze_sentiment, generate_workflow_diagram, auto_translate, save_translation_to_docx,
    generate_ppt, generate_audio_narration, create_transcript_index, query_transcript_index
)
from views.multimodal_rag.components import render_ppt_preview, generate_demo_questions

def render_text_tab():
    st.header("📝 Text Analysis & RAG")
    st.caption("Paste any text below to analyze sentiment, generate diagrams, and create presentations.")
    
    # Text Input
    raw_text = st.text_area("Input Text Content:", height=300, key="text_input_area")
    
    if st.button("🚀 Process Text", type="primary"):
        if not raw_text.strip():
            st.warning("Please enter some text first.")
        else:
            st.session_state.text_transcript = raw_text
            st.session_state.text_media_file = "text_rag_session"
            
            # Auto-Index
            create_transcript_index(raw_text, "text_rag_session")
            st.success("Text processed and indexed!")
            
    # Results
    if "text_transcript" in st.session_state:
        txt = st.session_state.text_transcript
        
        st.markdown("---")
        t_col1, t_col2 = st.columns([1, 1])
        
        with t_col1:
            st.subheader("🧠 Sentiment & Workflow")
            
            # Sentiment
            if st.button("Analyze Sentiment & Tone"):
                with st.spinner("Analyzing sentiment..."):
                    sentiment = analyze_sentiment(txt)
                    st.session_state.text_sentiment = sentiment
            
            if "text_sentiment" in st.session_state:
                st.markdown(st.session_state.text_sentiment)
                
            # Workflow Diagram
            st.markdown("---")
            if st.button("Generate Workflow Diagram"):
                with st.spinner("Generating Graphviz diagram..."):
                    wf_path = generate_workflow_diagram(txt, f"text_session_{len(txt)}")
                    if "Error" in wf_path:
                        st.error(wf_path)
                    else:
                        st.session_state.text_workflow_path = wf_path
                        st.success("Diagram Created!")
                        
            if "text_workflow_path" in st.session_state:
                st.image(st.session_state.text_workflow_path, caption="Generated Workflow", use_container_width=True)
                with open(st.session_state.text_workflow_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Diagram (.png)",
                        data=f,
                        file_name="workflow_diagram.png",
                        mime="image/png",
                        key="text_dl_wf"
                    )
                
        with t_col2:
            st.subheader("🌍 Translation & Docs")
            
            # Translate
            if st.button("Auto-Translate (En ↔ Fr)", key="text_trans_btn"):
                with st.spinner("Translating..."):
                    translation = auto_translate(txt)
                    st.session_state.text_translation = translation
            
            if "text_translation" in st.session_state:
                st.info(st.session_state.text_translation)
                
                # Word Export
                docx_path = save_translation_to_docx(st.session_state.text_translation, "text_rag_session")
                if docx_path and not "Error" in docx_path:
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Translation (.docx)",
                            data=f,
                            file_name="text_translation.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="text_dl_trans_docx"
                        )
            
            # PPT
            st.markdown("---")
            st.subheader("📊 Presentation")
            if st.button("Generate PPT", key="text_ppt_btn"):
                with st.spinner("Creating slides..."):
                    wf_path = st.session_state.get("text_workflow_path")
                    ppt_path, content = generate_ppt(txt, "text_rag_session", workflow_img_path=wf_path)
                    
                    if "Error" in ppt_path:
                        st.error(ppt_path)
                    else:
                        st.session_state.text_ppt_path = ppt_path
                        st.session_state.text_ppt_content = content
                        st.success("PPT Generated with Workflow!")
            
            if "text_ppt_path" in st.session_state:
                with open(st.session_state.text_ppt_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PPT",
                        data=f,
                        file_name="text_rag_presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key="text_dl_ppt"
                    )

                # ── PPT Slide Preview ──────────────────────────────────────────────
                if "text_ppt_content" in st.session_state:
                    render_ppt_preview(st.session_state.text_ppt_content)
                
                # Audio
                st.markdown("---")
                st.subheader("🎙️ Audio")
                voice = st.radio("Voice:", ["Gentleman", "Lady"], key="text_voice")
                if st.button("Generate Audio", key="text_audio_btn"):
                    with st.spinner("Generating audio..."):
                        audio_path = generate_audio_narration(
                            st.session_state.text_ppt_content,
                            voice,
                            "text_rag_session"
                        )
                        st.session_state.text_audio_path = audio_path
                
                if "text_audio_path" in st.session_state:
                    st.audio(st.session_state.text_audio_path)

        # Chat
        st.markdown("---")
        st.subheader("💬 Chat with Text")
        st.caption("You can ask a question using a different language.")

        if st.button("💡 Suggest demo questions", key="text_suggest_btn",
                     help="Generate sample questions from the indexed text"):
            with st.spinner("Thinking of questions..."):
                llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                st.session_state.text_suggested_qs = generate_demo_questions(txt, llm_id)

        if "text_suggested_qs" in st.session_state:
            tsq_cols = st.columns(2)
            for qi, q in enumerate(st.session_state.text_suggested_qs):
                if tsq_cols[qi % 2].button(q, key=f"text_sq_{qi}", use_container_width=True):
                    if "text_messages" not in st.session_state:
                        st.session_state.text_messages = []
                    st.session_state.text_messages.append({"role": "user", "content": q})
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    ans = query_transcript_index(q, "text_rag_session", model_name=llm_id)
                    st.session_state.text_messages.append({"role": "assistant", "content": ans})
                    st.rerun()

        if "text_messages" not in st.session_state:
            st.session_state.text_messages = []

        for msg in st.session_state.text_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about the text...", key="text_chat"):
            st.session_state.text_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    response = query_transcript_index(prompt, "text_rag_session", model_name=llm_id)
                    st.markdown(response)
                    st.session_state.text_messages.append({"role": "assistant", "content": response})
