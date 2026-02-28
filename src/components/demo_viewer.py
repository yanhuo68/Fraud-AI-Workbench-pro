import streamlit as st
from pathlib import Path
from PIL import Image
from config.settings import settings

def render_demo_viewer():
    """
    Renders an interactive full-screen-like overlay reading screenshots from `documentation/screen/`.
    Organized by category tabs with Next/Prev/Auto-play controls.
    """
    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #1f2c38 0%, #0d1117 100%);
                    border-radius: 16px; border-left: 6px solid #ff4b4b; margin-bottom: 2rem;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
            <h1 style='color: white; margin-bottom: 0.5rem;'>🎬 Sentinel Platform Tour</h1>
            <p style='color: #aaa; margin: 0; font-size: 1.1rem;'>
                Explore the features and interfaces of the Fraud Detection AI Workbench through interactive screenshots. 
                Use the tabs below to navigate by category.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Action Buttons ────────────────────────────────────────────────────
    col_spacer, col_dl, col_close = st.columns([6, 2, 2])
    
    with col_dl:
        zip_path = Path(__file__).parent.parent.parent / "documentation" / "compressed_demo.zip"
        if zip_path.exists():
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="📥 Download Demo (12MB)",
                    data=f,
                    file_name="Sentinel_Demo_Screenshots.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
    
    with col_close:
        if st.button("✖ Exit Demo Mode", use_container_width=True, type="primary"):
            st.session_state.show_demo_overlay = False
            st.rerun()

    # ── Discover Screenshots ──────────────────────────────────────────────
    # Base directory for screenshots
    screen_dir = Path(__file__).parent.parent.parent / "documentation" / "compressed-screen"
    
    if not screen_dir.exists() or not screen_dir.is_dir():
        st.error(f"Screenshot directory not found at `{screen_dir}`. Please verify the `documentation/compressed-screen/` folder exists.")
        return

    # Scan for category folders
    categories = []
    for item in screen_dir.iterdir():
        if item.is_dir():
            # Basic check to see if it has images
            images = list(item.glob("*.png")) + list(item.glob("*.jpg")) + list(item.glob("*.jpeg"))
            if images:
                # Format directory name ('llm_fine_tuning' -> 'LLM Fine Tuning')
                display_name = item.name.replace("_", " ").title()
                
                # Custom ordering: Put Security and Home first if they exist
                sort_weight = 100
                if "security" in item.name.lower(): sort_weight = 1
                elif "home" in item.name.lower(): sort_weight = 2
                elif "data" in item.name.lower(): sort_weight = 3
                
                categories.append({
                    "id": item.name,
                    "display": display_name,
                    "path": item,
                    "images": sorted(images, key=lambda x: x.stem), # Sort by filename alphabetically/numerically
                    "weight": sort_weight
                })
    
    # Sort categories based on weight, then alphabetically
    categories.sort(key=lambda x: (x["weight"], x["display"]))

    if not categories:
        st.info("No screenshot categories found. Add folders with `.png` or `.jpg` files inside `documentation/screen/`.")
        return

    # ── Render Tabs ───────────────────────────────────────────────────────
    tab_names = [cat["display"] for cat in categories]
    tabs = st.tabs(tab_names)

    # Initialize session state for active slide indices if they don't exist
    for cat in categories:
        state_key = f"demo_slide_idx_{cat['id']}"
        if state_key not in st.session_state:
            st.session_state[state_key] = 0

    # Build the UI inside each tab
    for idx, (tab, cat) in enumerate(zip(tabs, categories)):
        with tab:
            images = cat["images"]
            total_images = len(images)
            state_key = f"demo_slide_idx_{cat['id']}"
            
            # Retrieve current index for this category
            current_idx = st.session_state[state_key]
            
            # Failsafe in case files were deleted during session
            if current_idx >= total_images:
                current_idx = 0
                st.session_state[state_key] = 0

            # ── Callbacks for state management ────────────────────────
            def set_slide(c_id, new_val, t_images):
                idx = new_val % t_images
                st.session_state[f"demo_slide_idx_{c_id}"] = idx
                st.session_state[f"slider_{c_id}"] = idx + 1  # Sync the slider widget state!

            def on_slider_change(c_id, t_images):
                new_idx = st.session_state[f"slider_{c_id}"] - 1
                set_slide(c_id, new_idx, t_images)

            # ── Controls row ────────────────────────────────────────────
            c_prev, c_slide, c_next = st.columns([1.5, 7, 1.5])
            
            with c_prev:
                st.button(
                    "◀ Previous", 
                    key=f"prev_{cat['id']}", 
                    use_container_width=True, 
                    disabled=(total_images <= 1),
                    on_click=set_slide,
                    args=(cat['id'], current_idx - 1, total_images)
                )
            
            with c_slide:
                st.slider(
                    "Screenshot Progress",
                    min_value=1,
                    max_value=total_images,
                    value=current_idx + 1,
                    format="Slide %d",
                    key=f"slider_{cat['id']}",
                    label_visibility="collapsed",
                    on_change=on_slider_change,
                    args=(cat['id'], total_images)
                )
                    
            with c_next:
                st.button(
                    "Next ▶", 
                    key=f"next_{cat['id']}", 
                    use_container_width=True, 
                    disabled=(total_images <= 1),
                    on_click=set_slide,
                    args=(cat['id'], current_idx + 1, total_images)
                )
            
            st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

            # ── Image Rendering ─────────────────────────────────────────
            current_image_path = images[current_idx]
            
            # Simple wrapper card for the image
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 0.5rem;">
                    <span style="background: rgba(255,75,75,0.15); padding: 4px 12px; border-radius: 20px; color: #ffca28; font-weight: bold; border: 1px solid rgba(255,202,40,0.3);">
                        {current_idx + 1} / {total_images} &mdash; <code>{current_image_path.name}</code>
                    </span>
                </div>
            """, unsafe_allow_html=True)

            try:
                # Load and display image
                img = Image.open(current_image_path)
                st.image(img, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load image: {e}")



