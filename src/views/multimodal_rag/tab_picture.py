from views.multimodal_rag.components import render_multimodal_interface
from agents.multimodal_agent import describe_image

def render_picture_tab():
    render_multimodal_interface(
        tab_key="pic", 
        media_dir_path="data/pictureuploads", 
        allowed_exts=['.png', '.jpg', '.jpeg', '.webp'],
        process_func=describe_image,
        process_btn_label="👁️ Describe & Analyze",
        processing_msg="Analyzing Image with Vision AI..."
    )
