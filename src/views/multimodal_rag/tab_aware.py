import streamlit as st
import os
from pathlib import Path
from agents.multimodal_agent import (
    analyze_speaker_aware, analyze_time_aware, analyze_sentiment, analyze_confidence_aware,
    evaluate_retrieval_confidence
)

def render_aware_tab():
    st.header("🧠 Aware RAG")
    st.caption("Advanced analysis modes: Speaker, Time, Sentiment, & Confidence.")
    
    media_dir = Path("data/mediauploads")
    pic_dir = Path("data/pictureuploads")
    
    source_files = []
    if media_dir.exists():
        source_files.extend([f.name for f in media_dir.iterdir() if f.name != '.DS_Store'])
    if pic_dir.exists():
        source_files.extend([f.name for f in pic_dir.iterdir() if f.name != '.DS_Store'])
        
    if not source_files:
        st.info("No source files found in uploads.")
        return

    sel_source_file = st.selectbox("Select Content Source (Original File):", source_files, key="aware_file_select")
    
    if "aw_last_file" not in st.session_state or st.session_state.aw_last_file != sel_source_file:
        st.session_state.aw_last_file = sel_source_file
        for k in ["aw_spk_res", "aw_time_res", "aw_sent_res", "aw_qual_res", "aw_ret_q", "aw_show_trans"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
    
    TRANSCRIPT_DIR = Path("data/generated/transcripts")
    transcript_path = TRANSCRIPT_DIR / f"{sel_source_file}.txt"
    
    if not transcript_path.exists():
        st.warning(f"Analysis data not found for '{sel_source_file}'. Please go to 'Audio/Video RAG' or 'Picture RAG' to process it first.")
    else:
        aware_text = transcript_path.read_text()
        
        st.success(f"Ready to analyze '{sel_source_file}'!")
        
        with st.expander("View Source Text", expanded=False):
            st.text_area("Content", aware_text, height=200, key="aware_txt_preview")

        t1, t2, t3, t4 = st.tabs(["🗣️ Speaker-Aware", "⏳ Time-Aware", "❤️ Sentiment-Aware", "🛡️ Confidence-Aware"])
            
        with t1:
            st.subheader("🗣️ Speaker-Aware Analysis")
            st.caption("Identify speakers, dialogue patterns, and turn-taking.")
            if st.button("Analyze Speakers", key="aw_spk_btn"):
                with st.spinner("Analyzing dialogue..."):
                    res = analyze_speaker_aware(aware_text)
                    st.session_state.aw_spk_res = res
            if "aw_spk_res" in st.session_state: st.markdown(st.session_state.aw_spk_res)

        with t2:
            st.subheader("⏳ Time-Aware Analysis")
            st.caption("Extract timelines, dates, and event sequences.")
            if st.button("Analyze Timeline", key="aw_time_btn"):
                 with st.spinner("Extracting timeline..."):
                    res = analyze_time_aware(aware_text)
                    st.session_state.aw_time_res = res
            if "aw_time_res" in st.session_state: st.markdown(st.session_state.aw_time_res)

        with t3:
            st.subheader("❤️ Sentiment-Aware Analysis")
            st.caption("Deep dive into emotions and drivers.")
            if st.button("Analyze Sentiment", key="aw_sent_btn"):
                 with st.spinner("Analyzing emotions..."):
                    res = analyze_sentiment(aware_text)
                    st.session_state.aw_sent_res = res
            if "aw_sent_res" in st.session_state: st.markdown(st.session_state.aw_sent_res)

        with t4:
            st.subheader("🛡️ Confidence & Quality Control")
            
            if st.button("Analyze Content Quality", key="aw_qual_btn"):
                 with st.spinner("Assessing quality..."):
                    res = analyze_confidence_aware(aware_text)
                    st.session_state.aw_qual_res = res
            if "aw_qual_res" in st.session_state: st.markdown(st.session_state.aw_qual_res)
            
            st.markdown("---")
            st.write("**Retrieval Confidence Check**")
            st.caption("Check how well the vector store matches a query (Quality Control).")
            
            target_index_name = sel_source_file
            
            q_input = st.text_input("Test Retrieval (Enter Query):", key="aw_ret_q")
            if st.button("Check Retrieval Score", key="aw_ret_btn"):
                with st.spinner("Searching Vector Store..."):
                    ret_data = evaluate_retrieval_confidence(q_input, target_index_name)
                    if "error" in ret_data:
                        st.error(ret_data.get("error"))
                    else:
                        st.json(ret_data['top_results'])
