import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from utils.version_manager import DatasetManager, ModelManager
from agents.local_llm_discovery import list_ollama_models
from agents.llm_router import init_llm

def format_timestamp(ts) -> str:
    """Fallback format timestamp (if needed locally inside the tab)."""
    if not ts: return "N/A"
    try:
        if hasattr(ts, 'strftime'): return ts.strftime('%Y-%m-%d %H:%M')
        return str(ts)[:16].replace('T', ' ')
    except: return str(ts)[:16].replace('T', ' ')

def get_now_est():
    from datetime import timezone, timedelta
    return datetime.now(timezone(timedelta(hours=-5)))

def render_train_tab(is_admin, dataset_mgr: DatasetManager, model_mgr: ModelManager):
    st.header("Fine-Tuning 🔧")
    st.caption("Choose your training approach")
    
    st.markdown("---")
    st.subheader("📂 Training Configuration")
    
    col_tc1, col_tc2 = st.columns([2, 1])
    
    with col_tc1:
        all_datasets = dataset_mgr.get_all_datasets()
        for ds in all_datasets: dataset_mgr._update_sample_count(ds['id'])
        all_datasets = dataset_mgr.get_all_datasets()
        dataset_options = {f"{ds['name']} ({ds['sample_count']} samples)": ds['id'] for ds in all_datasets}
        
        selected_display = st.selectbox("📁 Training Dataset", options=list(dataset_options.keys()), help="Select which dataset to use for training")
        training_dataset_id = dataset_options[selected_display]
        training_ds = dataset_mgr.get_dataset(training_dataset_id)
    
    with col_tc2: st.metric("📄 Samples", training_ds['sample_count'])
    
    examples = dataset_mgr.get_samples(training_dataset_id)
    if not examples:
        st.warning("⚠️ Selected dataset is empty! Add samples in Tab 1.")
        st.stop()
    if len(examples) < 50: st.warning(f"⚠️ Only {len(examples)} examples. Recommend 50+ for quality.")
    
    st.markdown("---")
    st.subheader("📜 Model Registry")
    st.caption("Central managed repository of your trained LLM versions and their lineage.")
    all_models = model_mgr.get_all_models()
    
    if all_models:
        registry_data = []
        for model in all_models:
            ds_info = dataset_mgr.get_dataset(model['dataset_id'])
            ds_name = ds_info['name'] if ds_info else f"Unknown ({model['dataset_id']})"
            registry_data.append({
                "Model Name": model['name'],
                "Dataset Source": ds_name,
                "Base LLM": model.get('training_params', {}).get('base_model', 'N/A'),
                "Epochs": model.get('training_params', {}).get('epochs', 'N/A'),
                "Created": format_timestamp(model.get('created'))
            })
        st.dataframe(pd.DataFrame(registry_data), use_container_width=True, hide_index=True)
        
        with st.expander("🛠️ Manage Models"):
            for model in all_models:
                col_m1, col_m2 = st.columns([4, 1])
                with col_m1:
                    st.markdown(f"**{model['name']}**")
                    st.caption(f"ID: `{model['id']}` | Dataset: `{model['dataset_id']}`")
                with col_m2:
                    if st.button("🗑️ Delete", key=f"del_mod_{model['id']}", use_container_width=True):
                        model_mgr.delete_model(model['id'])
                        st.success(f"Deleted {model['name']}")
                        st.rerun()
    else: st.info("No training history yet. Train your first model below!")
    
    st.markdown("---")
    approach = st.radio("🎯 Select Training Approach", ["Option 1: MLX Fine-Tuning (True Model Training)", "Option 3: Ollama Expert Prompts (Smart Prompting)"], help="MLX = Download model + fine-tune | Ollama = Use models + expert prompts")
    st.markdown("---")
    
    if "MLX" in approach:
        st.subheader("⚙️ MLX Configuration")
        col1, col2, col3 = st.columns(3)
        with col1: model_base = st.selectbox("Base Model", ["mlx-community/Llama-3.2-1B-Instruct-4bit", "mlx-community/Qwen2.5-0.5B-Instruct-4bit"])
        with col2: epochs = st.slider("Epochs", 1, 10, 3)
        with col3: custom_model_name = st.text_input("Custom Version Name", placeholder="e.g., Llama-3.2-1B-Fraud-v1")
        
        st.markdown("---")
        st.subheader("🚀 Training")
        dataset_dir = "data/llm/mlx_dataset"
        dataset_file = f"{dataset_dir}/train.jsonl"
        
        col_tr1, col_tr2 = st.columns([2, 1])
        with col_tr1:
            st.info("💡 MLX training runs locally on your Mac.")
            if st.button("📥 Export Dataset for MLX", use_container_width=True):
                os.makedirs(dataset_dir, exist_ok=True)
                split_idx = int(len(examples) * 0.9)
                train_examples, valid_examples = examples[:split_idx], examples[split_idx:]
                
                with open(f"{dataset_dir}/train.jsonl", 'w') as f:
                    for ex in train_examples: f.write(json.dumps({"text": f"Transaction: {ex.get('input', '')}\\n\\nExpert Analysis: {ex.get('output', '')}"}) + '\\n')
                with open(f"{dataset_dir}/valid.jsonl", 'w') as f:
                    for ex in valid_examples: f.write(json.dumps({"text": f"Transaction: {ex.get('input', '')}\\n\\nExpert Analysis: {ex.get('output', '')}"}) + '\\n')
                
                st.success(f"✅ Exported {len(train_examples)} training + {len(valid_examples)} validation examples")
                st.info("📂 MLX dataset ready at: data/llm/mlx_dataset/")
                with st.expander("🔍 Preview first 3 JSONL records", expanded=True):
                    for _i, _ex in enumerate(train_examples[:3]):
                        st.code(json.dumps({"text": f"Transaction: {_ex.get('input', '')}\\n\\nExpert Analysis: {_ex.get('output', '')}"}, indent=2), language="json")
                        if _i < 2: st.divider()
        with col_tr2: st.metric("Training Iterations", epochs * 100)
        
        st.code(f"mlx_lm.lora --model {model_base} --train --data {dataset_dir} --iters {epochs*100}", language="bash")
        
        if is_admin: train_btn = st.button("🚀 Start Training", type="primary", use_container_width=True)
        else: st.button("🚀 Start Training", type="primary", use_container_width=True, disabled=True, help="Admin access required"); train_btn = False
        
        if train_btn:
            if not os.path.exists(dataset_file): st.error("⚠️ Export dataset first!")
            else:
                st.info("🔄 Starting MLX training... This will take 15-30 minutes.")
                if "tasks" not in st.session_state: st.session_state.tasks = []
                task_id = f"mlx_{int(datetime.now().timestamp())}"
                st.session_state.tasks.append({"id": task_id, "name": f"MLX Fine-Tuning: {custom_model_name or model_base}", "status": "running", "progress": 0.1, "timestamp": datetime.now().strftime("%H:%M:%S")})
                
                with st.spinner("Training in progress..."):
                    try:
                        import subprocess
                        result = subprocess.run(['mlx_lm.lora', '--model', model_base, '--train', '--data', dataset_dir, '--iters', str(epochs*100)], capture_output=True, text=True, timeout=1800)
                        if result.returncode == 0:
                            try:
                                model_name = custom_model_name or f"MLX_{model_base.split('/')[-1]}_{get_now_est().strftime('%m%d_%H%M')}"
                                model_id = model_mgr.register_model(name=model_name, dataset_id=training_dataset_id, training_params={"epochs": epochs, "iterations": epochs * 100, "base_model": model_base})
                                target_path = model_mgr.get_model_path(model_id).parent / "adapters"
                                target_path.parent.mkdir(parents=True, exist_ok=True)
                                if os.path.exists("./adapters"):
                                    import shutil; shutil.move("./adapters", target_path)
                                st.success(f"✅ Training complete! Registered model: {model_name}")
                                st.balloons()
                            except Exception as reg_err: st.error(f"⚠️ Training succeeded but registration failed: {reg_err}")
                        else:
                            st.error(f"❌ Training failed: {result.stderr}")
                            for t in st.session_state.tasks:
                                if t["id"] == task_id: t["status"] = "failed"
                    except subprocess.TimeoutExpired: st.error("⏱️ Training timeout (>30 min). Check terminal for status.")
                    except FileNotFoundError: st.error("❌ MLX not found. Install it: `pip install mlx-lm`")
                    except Exception as e: st.error(f"❌ Error: {e}")
        st.markdown("---")
        st.caption("🕒 **Training Time:** ~15-30 minutes | **Cost:** $0.00")
        
    else:
        st.subheader("🧠 Ollama Expert Prompt Builder")
        st.info("🔍 Detecting your Ollama models...")
        try:
            ollama_models = list_ollama_models()
            if ollama_models:
                model_names = [m.replace("local_ollama:", "") for m in ollama_models]
                st.success(f"✅ Found {len(model_names)} Ollama models")
                selected_ollama = st.selectbox("Select Ollama Model", model_names)
            else: st.warning("No Ollama models detected."); selected_ollama = None
        except Exception as e: st.warning(f"Could not connect to Ollama API: {e}"); selected_ollama = None
        
        st.markdown("---")
        st.subheader("📝 Expert Prompt Template")
        st.caption("Auto-generated from your expert feedback examples:")
        categories = [ex.get('category', '') for ex in examples]
        most_common_cat = pd.Series(categories).value_counts().index[0] if categories else "Account Takeover"
        expert_prompt = f"You are an expert fraud analyst. Analyze the following transaction and provide a detailed fraud assessment.\n\n**Expert Guidelines (learned from {len(examples)} reviewed cases):**\n1. **Most Common Fraud Type:** {most_common_cat}\n2. **Key Risk Indicators:**\n   - Previous fraud history (highest priority)\n   - Transaction velocity (>10 txns/24h = suspicious)\n   - New accounts (<30 days) with high amounts (>$5000)\n   - Account age >90 days = lower baseline risk\n3. **Decision Framework:**\n   - HIGH RISK (>70% prob): BLOCK + investigate\n   - MEDIUM RISK (30-70%): Hold + step-up auth\n   - LOW RISK (<30%): Approve + monitor\n4. **Output Format:**\n   - List specific red flags found\n   - Provide clear BLOCK/REVIEW/APPROVE recommendation\n   - Explain reasoning based on evidence\n\nNow analyze this transaction:\n{{TRANSACTION_DATA}}\n"
        st.text_area("Expert Prompt Template", expert_prompt, height=300)
        
        if selected_ollama:
            st.markdown("---")
            st.subheader("🧪 Test & Register")
            col_reg1, col_reg2 = st.columns([2, 1])
            with col_reg1: custom_ollama_name = st.text_input("Expert Version Name", placeholder=f"OllamaExpert_{training_ds['name'].replace(' ', '_')}")
            with col_reg2:
                if is_admin: reg_btn = st.button("💾 Register as Version", use_container_width=True)
                else: st.button("💾 Register as Version", use_container_width=True, disabled=True); reg_btn = False
                if reg_btn:
                    try:
                        name_to_save = custom_ollama_name or f"OllamaExpert_{training_ds['id']}_{get_now_est().strftime('%m%d_%H%M')}"
                        model_mgr.register_model(name=name_to_save, dataset_id=training_dataset_id, training_params={"type": "ollama_expert", "base_model": f"ollama:{selected_ollama}", "prompt_template": expert_prompt})
                        st.success(f"✅ Registered expert version: {name_to_save}")
                        st.balloons(); st.rerun()
                    except Exception as e: st.error(f"❌ Registration failed: {e}")
            
            st.markdown("---")
            if st.button("🚀 Test with Sample Transaction", type="primary", use_container_width=True):
                sample_txn = examples[0] if examples else {}
                txn_data = f"Amount: ${sample_txn.get('fraud_probability', 0)*10000:,.2f}\nProbability: {sample_txn.get('fraud_probability', 0):.1%}\nAccount Age: 45 days\nVelocity: 3 txns/24h\nPrevious Fraud: 0"
                test_prompt = expert_prompt.replace("{{TRANSACTION_DATA}}", txn_data)
                st.info(f"🔄 Running inference with {selected_ollama}...")
                with st.spinner("Generating response..."):
                    try:
                        llm = init_llm(f"ollama:{selected_ollama}")
                        response = llm.invoke(test_prompt)
                        st.success("✅ Ollama Response:")
                        st.text_area("Expert-Guided Analysis", response.content, height=300)
                        st.info("🎯 This prompt will be used in Tab 4 for all comparisons!")
                    except Exception as e: st.error(f"❌ Ollama API error: {e}")
        st.markdown("---")
        st.info("✅ **Ready to use!** This prompt will be applied in Tab 4 for instant expert-guided analysis.")
