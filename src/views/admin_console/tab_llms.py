import streamlit as st
import os
import shutil
import json

def render_llms_tab():
    from utils.ollama_manager import get_ollama_models, pull_ollama_model, delete_ollama_model, check_ollama_connection
    
    st.header("🤖 Local LLM Management (Ollama)")
    
    # Prerequisite & Disk Info
    col_info, col_disk = st.columns([2, 1])
    with col_info:
        st.info("⚠️ **Prerequisite**: You must have [Ollama](https://ollama.com) installed and running on your host machine.")
        st.markdown("Default Connection: `http://host.docker.internal:11434` (configurable via `OLLAMA_BASE_URL`)")
    
    with col_disk:
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        st.metric("Container Free Space", f"{free_gb:.2f} GB", help="Approximate available space for new models (if using shared volume).")
    
    # Connection Check
    if not check_ollama_connection():
        st.error("⚠️ Could not connect to Ollama. Please ensure it is running.")
        st.caption(f"Trying to connect to: `{os.environ.get('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')}`")
    else:
        st.success("✅ Connected to Ollama")
        
        # 1. List Models
        st.subheader("Installed Models")
        models = get_ollama_models()
        
        if not models:
            st.warning("No models installed.")
        else:
            # Table Layout
            header = st.columns([3, 2, 2, 1])
            header[0].markdown("**Model Name**")
            header[1].markdown("**Size**")
            header[2].markdown("**Modified**")
            header[3].markdown("**Action**")
            st.markdown("---")
            
            for m in models:
                row = st.columns([3, 2, 2, 1])
                row[0].code(m["name"], language="text")
                row[1].write(m["size"])
                row[2].write(m["modified"])
                
                if row[3].button("🗑️", key=f"del_llm_{m['name']}"):
                    with st.spinner(f"Deleting {m['name']}..."):
                        if delete_ollama_model(m["name"]):
                            st.success(f"Deleted {m['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                st.markdown("---")
        
        # 2. Pull New Model
        st.subheader("⬇️ Pull New Model")
        
        # Recommended Small Models
        RECOMMENDED_MODELS = {
            "Custom...": "",
            "Llama 3 (4.7 GB)": "llama3",
            "Mistral (4.1 GB)": "mistral",
            "Gemma 2B (1.5 GB)": "gemma:2b",
            "Phi-3 Mini (2.3 GB)": "phi3",
            "Qwen2 0.5B (350 MB)": "qwen2:0.5b",
            "TinyLlama (600 MB)": "tinyllama"
        }
        
        with st.form("pull_model_form"):
            col_sel, col_inp = st.columns(2)
            
            with col_sel:
                selected_opt = st.selectbox("Select Recommended Model", options=list(RECOMMENDED_MODELS.keys()), index=1)
            
            with col_inp:
                manual_input = st.text_input("Or enter generic Model Tag", value=RECOMMENDED_MODELS[selected_opt], disabled=(selected_opt != "Custom..."))
            
            # Logic to determine actual model to pull
            final_model_to_pull = manual_input if selected_opt == "Custom..." else RECOMMENDED_MODELS[selected_opt]
            if selected_opt == "Custom..." and not manual_input:
                 final_model_to_pull = "" 
            
            # Display size check warning if tight? (Optional)
            
            submitted = st.form_submit_button("Pull Model")
            
            if submitted:
                if not final_model_to_pull:
                     st.error("Please select or enter a model name.")
                else: 
                    status_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    status_text.info(f"Starting pull for {final_model_to_pull}...")
                    
                    # Streaming Pull
                    stream = pull_ollama_model(final_model_to_pull)
                    if stream:
                        last_status = ""
                        for line in stream:
                            try:
                                # Parse JSON line
                                data = json.loads(line)
                                status = data.get("status", "")
                                
                                # Simple progress estimation based on status text or specific fields if available
                                # Ollama returns 'total' and 'completed' bytes
                                total = data.get("total")
                                completed = data.get("completed")
                                
                                if total and completed:
                                    pct = float(completed) / float(total)
                                    progress_bar.progress(pct)
                                
                                if status != last_status:
                                    status_text.text(f"{status}...")
                                    last_status = status
                                    
                            except:
                                pass
                        
                        progress_bar.progress(1.0)
                        status_text.success(f"Successfully pulled {final_model_to_pull}!")
                        st.rerun()
                    else:
                        status_text.error(f"Failed to start pull for {final_model_to_pull}. Check logs/connection.")
