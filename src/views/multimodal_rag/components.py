import streamlit as st
import os
from pathlib import Path
from agents.multimodal_agent import (
    create_transcript_index, query_transcript_index, generate_ppt, generate_audio_narration,
    auto_translate, save_translation_to_docx, analyze_transcript
)

# ──────────────────────────────────────────────────────────────
# HELPER: PPT Slide Preview
# ──────────────────────────────────────────────────────────────
def render_ppt_preview(content: dict):
    """Render a visual card-based preview of the generated PPT content dict."""
    if not content:
        return
    with st.expander("📊 Slide Preview", expanded=True):
        # Title slide
        st.markdown(
            f"<div style='background:#003f88;color:white;padding:14px 20px;border-radius:8px;margin-bottom:10px;'>"
            f"<h3 style='margin:0'>{content.get('title','Untitled')}</h3>"
            f"<p style='margin:4px 0 0;opacity:.8;font-size:0.9em'>{content.get('subtitle','')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Agenda
        agenda = content.get("agenda", [])
        if agenda:
            with st.container():
                st.markdown("**🗒 Agenda**")
                for item in agenda:
                    st.markdown(f"- {item}")

        # Key-point slides
        key_points = content.get("key_points", [])
        if key_points:
            kp_cols = st.columns(min(len(key_points), 3))
            for i, section in enumerate(key_points):
                with kp_cols[i % 3]:
                    st.markdown(
                        f"<div style='border:1px solid #ddd;border-radius:6px;padding:10px;min-height:100px;'>"
                        f"<b>{section.get('slide_title','')}</b><ul>"
                        + "".join(f"<li>{p}</li>" for p in section.get("points", []))
                        + "</ul></div>",
                        unsafe_allow_html=True
                    )

        # AI Insights
        insights = content.get("ai_insight", [])
        if insights:
            st.markdown("**🤖 AI Insights**")
            for ins in insights:
                st.info(ins)

        # Conclusion
        conclusion = content.get("conclusion", "")
        if conclusion:
            st.success(f"🎯 **Conclusion:** {conclusion}")

# ──────────────────────────────────────────────────────────────
# HELPER: Generate demo questions from indexed content
# ──────────────────────────────────────────────────────────────
def generate_demo_questions(text: str, llm_id: str = "gpt-4o-mini", n: int = 4) -> list[str]:
    """Ask the LLM to generate n interesting questions from the given content snippet."""
    from agents.llm_router import init_llm
    try:
        llm = init_llm(llm_id)
        snippet = text[:6000]  # keep prompt under token limits
        prompt = (
            f"You are an expert analyst reviewing the following content.\n\n"
            f"\"\"\"{snippet}\"\"\"\n\n"
            f"Generate exactly {n} specific, insightful questions a user might ask about this content. "
            f"Focus on key facts, patterns, entities, or anomalies present in the text. "
            f"Output ONLY the {n} questions, one per line, no numbering or extra text."
        )
        resp = llm.invoke(prompt)
        qs = [line.strip().lstrip("- 0123456789.") for line in resp.content.strip().split("\n") if line.strip()]
        return qs[:n]
    except Exception as e:
        return [f"Error generating questions: {e}"]

# ──────────────────────────────────────────────────────────────
# REUSABLE COMPONENT: Multimodal Audio/Video/Picture RAG
# ──────────────────────────────────────────────────────────────
def render_multimodal_interface(tab_key, media_dir_path, allowed_exts, process_func, process_btn_label, processing_msg):
    MEDIA_DIR = Path(media_dir_path)

    if not MEDIA_DIR.exists():
        st.info(f"No '{media_dir_path}' directory found. Please upload files first.")
        return

    files = [f.name for f in MEDIA_DIR.iterdir() if f.name != '.DS_Store' and f.suffix.lower() in allowed_exts]
    if not files:
        st.info(f"No matching files found in '{media_dir_path}'. Go to 'Data Hub' to add some!")
        return

    # ── Batch Processing Mode Toggle ────────────────────────────────────────
    batch_mode = st.toggle("⚡ Batch Processing Mode", key=f"{tab_key}_batch_toggle",
                           help="Process ALL files in this folder in one click")

    if batch_mode:
        st.info(f"**Batch Mode** — {len(files)} file(s) found. Click below to process all of them.")
        if st.button(f"🚀 Process All {len(files)} Files", key=f"{tab_key}_batch_btn", type="primary"):
            batch_results = []
            prog = st.progress(0, text="Starting batch...")
            for i, fname in enumerate(files):
                prog.progress((i) / len(files), text=f"Processing {fname} ({i+1}/{len(files)})...")
                fpath = str(MEDIA_DIR / fname)
                try:
                    result = process_func(fpath)
                    status = "✅" if "Error" not in result else "❌"
                    batch_results.append({"File": fname, "Status": status, "Characters": len(result) if "Error" not in result else 0})
                    if "Error" not in result:
                        create_transcript_index(result, fname)
                except Exception as e:
                    batch_results.append({"File": fname, "Status": "❌", "Characters": 0})
            prog.progress(1.0, text="Batch complete!")
            import pandas as pd
            st.dataframe(pd.DataFrame(batch_results), use_container_width=True)
            st.success(f"Batch complete! Processed {sum(1 for r in batch_results if r['Status'] == '✅')}/{len(files)} files successfully.")
        st.markdown("---")
        st.markdown("**⬇ Now select a specific file below to Transcribe & Analyze it individually:**")

    # ── Single-File Mode (always shown; follows batch summary when active) ──
    # Prefix for session state keys to keep tabs independent
    # e.g. "av_" or "pic_"
    p = tab_key 

    # Select File
    selected_file = st.selectbox(f"Select File ({tab_key}):", files, key=f"{p}_select")
    
    # Auto-Clear Logic
    last_sel_key = f"{p}_last_selected"
    if last_sel_key not in st.session_state:
        st.session_state[last_sel_key] = selected_file

    if st.session_state[last_sel_key] != selected_file:
        # Clear specific tab keys
        keys_to_clear = [
            f'{p}_summary', f'{p}_minutes', f'{p}_translation', 
            f'{p}_messages', f'{p}_ppt_path', f'{p}_ppt_content', f'{p}_audio_path',
            f'{p}_transcript', f'{p}_media_file'
        ]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state[last_sel_key] = selected_file
        st.rerun()

    file_path = MEDIA_DIR / selected_file
    
    # Layout: Preview + Controls
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Preview")
        ext = file_path.suffix.lower()
        if ext in ['.mp3', '.wav', '.ogg']:
            st.audio(str(file_path))
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            st.video(str(file_path))
        elif ext in ['.png', '.jpg', '.jpeg', '.webp']:
            st.image(str(file_path), use_container_width=True)
        else:
            st.warning(f"Preview not supported for {ext}")

    with c2:
        st.subheader("Actions")
        if st.button(process_btn_label, key=f"{p}_process_btn", type="primary"):
            with st.spinner(processing_msg):
                text = process_func(str(file_path))
                
                if "Error" in text:
                    st.error(text)
                else:
                    st.session_state[f'{p}_transcript'] = text
                    st.session_state[f'{p}_media_file'] = selected_file
                    
                    # Clear prev analysis
                    for k in [f'{p}_summary', f'{p}_minutes', f'{p}_translation', f'{p}_messages']:
                        if k in st.session_state: del st.session_state[k]
                    
                    # Auto-Index
                    create_transcript_index(text, selected_file)
                    
                    st.success("Analysis & Indexing Complete!")
                    st.rerun()

    # Results Section
    transcript_key = f'{p}_transcript'
    if transcript_key in st.session_state and st.session_state.get(f'{p}_media_file') == selected_file:
        transcript = st.session_state[transcript_key]
        
        st.markdown("---")
        res_col1, res_col2 = st.columns([2, 1])
        
        with res_col1:
            st.subheader("📜 Content Description")
            st.text_area("Full Text", transcript, height=400, key=f"{p}_txt_area")
            
            st.download_button(
                label="Download Text (.txt)",
                data=transcript,
                file_name=f"{selected_file}.txt",
                mime="text/plain",
                key=f"{p}_dl_txt"
            )
            
            # Translation
            st.subheader("🌍 Translation")
            if st.button("Auto-Translate (En ↔ Fr)", key=f"{p}_trans_btn"):
                with st.spinner("Translating..."):
                    translation = auto_translate(transcript)
                    st.session_state[f'{p}_translation'] = translation
            
            if f'{p}_translation' in st.session_state:
                st.info(st.session_state[f'{p}_translation'])
                
                # Word Export
                docx_path = save_translation_to_docx(st.session_state[f'{p}_translation'], Path(selected_file).stem)
                if docx_path and not "Error" in docx_path:
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Translation (.docx)",
                            data=f,
                            file_name=f"{Path(selected_file).stem}_translation.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"{p}_dl_trans_docx"
                        )
            
        with res_col2:
            st.subheader("🧠 AI Insights")
            
            tab_sum, tab_min = st.tabs(["Summary", "Meeting Minutes"])
            
            with tab_sum:
                if st.button("Generate Summary", key=f"{p}_sum_btn"):
                    with st.spinner("Summarizing..."):
                        summary = analyze_transcript(transcript, "summary")
                        st.session_state[f'{p}_summary'] = summary
                
                if f'{p}_summary' in st.session_state:
                    st.markdown(st.session_state[f'{p}_summary'])
                    
            with tab_min:
                if st.button("Generate Minutes", key=f"{p}_min_btn"):
                    with st.spinner("Drafting minutes..."):
                        minutes = analyze_transcript(transcript, "minutes")
                        st.session_state[f'{p}_minutes'] = minutes
                
                if f'{p}_minutes' in st.session_state:
                    st.markdown(st.session_state[f'{p}_minutes'])
                    
            # PPT Generation
            st.markdown("---")
            st.subheader("📊 Presentation")
            if st.button("Generate PPT", key=f"{p}_ppt_btn"):
                with st.spinner("Creating slides..."):
                    ppt_path, content = generate_ppt(transcript, Path(selected_file).stem)
                    if "Error" in ppt_path:
                        st.error(ppt_path)
                    else:
                        st.session_state[f'{p}_ppt_path'] = ppt_path
                        st.session_state[f'{p}_ppt_content'] = content
                        st.success("PPT Generated!")
            
            if f'{p}_ppt_path' in st.session_state:
                with open(st.session_state[f'{p}_ppt_path'], "rb") as f:
                    st.download_button(
                        label="⬇️ Download PPT",
                        data=f,
                        file_name=os.path.basename(st.session_state[f'{p}_ppt_path']),
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key=f"{p}_dl_ppt"
                    )

                # ── PPT Slide Preview ─────────────────────────────────────────
                if f'{p}_ppt_content' in st.session_state:
                    render_ppt_preview(st.session_state[f'{p}_ppt_content'])
                
                # Audio Narration
                st.markdown("---")
                st.subheader("🎙️ Audio Narration")
                voice = st.radio("Select Voice:", ["Gentleman", "Lady"], key=f"{p}_voice")
                
                if st.button("Generate Audio", key=f"{p}_audio_btn"):
                    if f'{p}_ppt_content' not in st.session_state:
                        st.warning("Please regenerate PPT first.")
                    else:
                        with st.spinner("Generating audio..."):
                            audio_path = generate_audio_narration(
                                st.session_state[f'{p}_ppt_content'],
                                voice,
                                Path(selected_file).stem
                            )
                            if "Error" in audio_path:
                                st.error(audio_path)
                            else:
                                st.session_state[f'{p}_audio_path'] = audio_path
                                st.success("Audio Created!")
                
                if f'{p}_audio_path' in st.session_state:
                    st.audio(st.session_state[f'{p}_audio_path'])
                    with open(st.session_state[f'{p}_audio_path'], "rb") as f:
                        st.download_button(
                            label="⬇️ Download Audio",
                            data=f,
                            file_name=os.path.basename(st.session_state[f'{p}_audio_path']),
                            mime="audio/mpeg",
                            key=f"{p}_dl_audio"
                        )

        # Chat
        st.markdown("---")
        st.subheader("💬 Chat with Content")
        st.caption("You can ask a question using a different language.")

        # ── Suggest Demo Questions ────────────────────────────────────────────
        sq_key = f"{p}_suggested_qs"
        if st.button("💡 Suggest demo questions", key=f"{p}_suggest_btn",
                     help="Generate sample questions from the indexed content"):
            with st.spinner("Thinking of questions..."):
                llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                st.session_state[sq_key] = generate_demo_questions(transcript, llm_id)

        if sq_key in st.session_state:
            sq_cols = st.columns(2)
            for qi, q in enumerate(st.session_state[sq_key]):
                if sq_cols[qi % 2].button(q, key=f"{p}_sq_{qi}", use_container_width=True):
                    # Inject as a user message immediately
                    msgs_key2 = f'{p}_messages'
                    if msgs_key2 not in st.session_state:
                        st.session_state[msgs_key2] = []
                    st.session_state[msgs_key2].append({"role": "user", "content": q})
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    ans = query_transcript_index(q, selected_file, model_name=llm_id)
                    st.session_state[msgs_key2].append({"role": "assistant", "content": ans})
                    st.rerun()

        msgs_key = f'{p}_messages'
        if msgs_key not in st.session_state:
            st.session_state[msgs_key] = []

        for msg in st.session_state[msgs_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a question...", key=f"{p}_chat_input"):
            st.session_state[msgs_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")
                    response = query_transcript_index(prompt, selected_file, model_name=llm_id)
                    st.markdown(response)
                    st.session_state[msgs_key].append({"role": "assistant", "content": response})
