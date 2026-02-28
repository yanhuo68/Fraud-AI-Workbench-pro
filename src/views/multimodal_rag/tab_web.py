import streamlit as st
import os
from pathlib import Path
from agents.multimodal_agent import (
    scrape_web_content, analyze_sentiment, generate_workflow_diagram, auto_translate,
    save_translation_to_docx, generate_ppt, generate_audio_narration, create_transcript_index,
    query_transcript_index
)
from views.multimodal_rag.components import render_ppt_preview, generate_demo_questions

def render_web_tab():
    st.header("🌐 Web Content RAG")

    with st.expander("⚠️ Web Scraping Limitations & Tips", expanded=False):
        st.markdown("""
| Limitation | Details |
|---|---|
| **JavaScript-heavy pages** | Pages that load content via JS (YouTube, Twitter/X, SPAs) cannot be scraped — only static HTML is accessible |
| **Paywalled / Login-gated** | Pages behind authentication or paywalls will return empty or login form text |
| **Bot protection (Cloudflare, etc.)** | Some sites block automated requests with CAPTCHAs; you may receive a 403 error |
| **Rate limiting** | Repeatedly scraping the same domain may result in temporary IP bans |
| **Content size** | Very large pages will be truncated to the first ~15,000 characters for LLM analysis |

**✅ Works well with:** News articles, Wikipedia, government sites, blog posts, documentation pages.

**Tips:**
- If scraping fails, try copying & pasting the article text into the **Text RAG** tab instead.
- For dynamic content, use your browser’s *Reader Mode* to get a clean print version URL.
        """)
    st.caption("Analyze a webpage directly. Extract content, specific knowledge, and generate reports.")
    
    default_url = "https://www.thecanadianpressnews.ca/business/young-canadians-tell-of-their-generations-challenges-and-hopes/article_5b442646-11fc-53f0-a54f-dca9835a7286.html"
    url_input = st.text_input("Enter Web URL:", value=default_url, key="web_url_input")
    
    if st.button("🚀 Process URL", type="primary", key="web_process_btn"):
        if not url_input.strip():
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Scraping webpage..."):
                web_text = scrape_web_content(url_input)
                
                if "Error" in web_text:
                    st.error(web_text)
                else:
                    st.session_state.web_transcript = web_text
                    st.session_state.web_media_file = "web_rag_session"
                    
                    create_transcript_index(web_text, "web_rag_session")
                    st.success("Web content extracted and indexed!")

    if "web_transcript" in st.session_state:
        w_txt = st.session_state.web_transcript
        
        with st.expander("View Scraped Content", expanded=False):
            st.text_area("Content", w_txt, height=200)
            
        st.markdown("---")
        w_col1, w_col2 = st.columns([1, 1])
        
        with w_col1:
            st.subheader("🧠 Sentiment & Workflow")
            
            if st.button("Analyze Sentiment", key="web_sent_btn"):
                with st.spinner("Analyzing..."):
                    sentiment = analyze_sentiment(w_txt)
                    st.session_state.web_sentiment = sentiment
            
            if "web_sentiment" in st.session_state:
                st.markdown(st.session_state.web_sentiment)
                
            st.markdown("---")
            if st.button("Generate Workflow", key="web_wf_btn"):
                with st.spinner("Generating Diagram..."):
                    wf_path = generate_workflow_diagram(w_txt, f"web_session_{len(w_txt)}")
                    if "Error" in wf_path:
                        st.error(wf_path)
                    else:
                        st.session_state.web_workflow_path = wf_path
                        st.success("Diagram Created!")
                        
            if "web_workflow_path" in st.session_state:
                st.image(st.session_state.web_workflow_path, use_container_width=True)
                with open(st.session_state.web_workflow_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Diagram",
                        data=f,
                        file_name="web_workflow.png",
                        mime="image/png",
                        key="web_dl_wf"
                    )
                    
        with w_col2:
            st.subheader("🌍 Translation & Docs")
            
            if st.button("Auto-Translate", key="web_trans_btn"):
                with st.spinner("Translating..."):
                    val = auto_translate(w_txt)
                    st.session_state.web_translation = val
            
            if "web_translation" in st.session_state:
                st.info(st.session_state.web_translation)
                docx_path = save_translation_to_docx(st.session_state.web_translation, "web_rag_session")
                if docx_path and not "Error" in docx_path:
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download (.docx)",
                            data=f,
                            file_name="web_translation.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="web_dl_docx"
                        )
            
            st.markdown("---")
            st.subheader("📊 Presentation")
            if st.button("Generate PPT", key="web_ppt_btn"):
                with st.spinner("Creating..."):
                    wf_path = st.session_state.get("web_workflow_path")
                    ppt_path, content = generate_ppt(w_txt, "web_rag_session", workflow_img_path=wf_path)
                    if "Error" in ppt_path:
                        st.error(ppt_path)
                    else:
                        st.session_state.web_ppt_path = ppt_path
                        st.session_state.web_ppt_content = content
                        st.success("PPT Ready!")
            
            if "web_ppt_path" in st.session_state:
                with open(st.session_state.web_ppt_path, "rb") as f:
                    st.download_button("⬇️ Download PPT", f, "web_presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", key="web_dl_ppt")

                if "web_ppt_content" in st.session_state:
                    render_ppt_preview(st.session_state.web_ppt_content)

                st.markdown("---")
                voice = st.radio("Voice:", ["Gentleman", "Lady"], key="web_voice")
                if st.button("Generate Audio", key="web_audio_btn"):
                    with st.spinner("Speaking..."):
                        audio_path = generate_audio_narration(st.session_state.web_ppt_content, voice, "web_rag_session")
                        st.session_state.web_audio_path = audio_path
                
                if "web_audio_path" in st.session_state:
                    st.audio(st.session_state.web_audio_path)

        st.markdown("---")
        st.subheader("💬 Chat with Web Content")
        st.caption("You can ask a question using a different language.")

        if st.button("💡 Suggest demo questions", key="web_suggest_btn",
                     help="Generate sample questions from the web content"):
            with st.spinner("Thinking of questions..."):
                llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                st.session_state.web_suggested_qs = generate_demo_questions(w_txt, llm_id)

        if "web_suggested_qs" in st.session_state:
            wsq_cols = st.columns(2)
            for qi, q in enumerate(st.session_state.web_suggested_qs):
                if wsq_cols[qi % 2].button(q, key=f"web_sq_{qi}", use_container_width=True):
                    if "web_messages" not in st.session_state:
                        st.session_state.web_messages = []
                    st.session_state.web_messages.append({"role": "user", "content": q})
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    ans = query_transcript_index(q, "web_rag_session", model_name=llm_id)
                    st.session_state.web_messages.append({"role": "assistant", "content": ans})
                    st.rerun()

        if "web_messages" not in st.session_state:
            st.session_state.web_messages = []

        for msg in st.session_state.web_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about the website...", key="web_chat"):
            st.session_state.web_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    response = query_transcript_index(prompt, "web_rag_session", model_name=llm_id)
                    st.markdown(response)
                    st.session_state.web_messages.append({"role": "assistant", "content": response})
