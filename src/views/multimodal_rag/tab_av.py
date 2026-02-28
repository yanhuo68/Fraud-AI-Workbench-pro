from views.multimodal_rag.components import render_multimodal_interface
from agents.multimodal_agent import transcribe_audio

def render_av_tab():
    render_multimodal_interface(
        tab_key="av", 
        media_dir_path="data/mediauploads", 
        allowed_exts=['.mp3', '.wav', '.ogg', '.mp4', '.mov', '.avi', '.mkv'],
        process_func=transcribe_audio,
        process_btn_label="📝 Transcribe & Analyze",
        processing_msg="Transcribing Audio/Video..."
    )
