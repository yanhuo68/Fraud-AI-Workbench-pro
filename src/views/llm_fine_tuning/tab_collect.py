import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
from utils.version_manager import DatasetManager

def render_collect_tab(is_admin, dataset_mgr: DatasetManager):
    st.header("Step 1: Collect Expert Feedback 📝")
    st.caption("Review AI-generated explanations and provide corrections to build training data.")
    
    DATASET_DIR = Path("data/llm")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_FILE = DATASET_DIR / "finetune_dataset.jsonl"
    
    # Dataset Management Section
    st.markdown("---")
    st.subheader("📂 Dataset Selection")
    
    col_ds1, col_ds2, col_ds3 = st.columns([3, 2, 1])
    
    with col_ds1:
        all_datasets = dataset_mgr.get_all_datasets()
        active_dataset_id = dataset_mgr.get_active_dataset()
        
        if all_datasets:
            for ds in all_datasets:
                dataset_mgr._update_sample_count(ds['id'])
            all_datasets = dataset_mgr.get_all_datasets()
            dataset_options = {f"{ds['name']} ({ds['sample_count']} samples)": ds['id'] for ds in all_datasets}
            
            current_name = next((k for k, v in dataset_options.items() if v == active_dataset_id), list(dataset_options.keys())[0])
            
            selected_display = st.selectbox(
                "📁 Active Dataset",
                options=list(dataset_options.keys()),
                index=list(dataset_options.keys()).index(current_name) if current_name in dataset_options else 0,
                help="Samples will be added to this dataset"
            )
            
            selected_id = dataset_options[selected_display]
            if selected_id != active_dataset_id:
                dataset_mgr.set_active_dataset(selected_id)
                st.success(f"✅ Switched to: {selected_display}")
                st.rerun()
        else:
            st.warning("⚠️ No datasets found. Create one below.")
            selected_id = None
    
    with col_ds2:
        active_ds = dataset_mgr.get_dataset(active_dataset_id) if active_dataset_id else None
        if active_ds:
            st.metric("📄 Samples", active_ds['sample_count'])
    
    with col_ds3:
        if is_admin:
            if st.button("➕ New Dataset", use_container_width=True):
                st.session_state['show_create_dataset'] = True
        else:
            st.button("➕ New Dataset", use_container_width=True, disabled=True, help="Administrator access required to create datasets")
    
    if st.session_state.get('show_create_dataset', False):
        with st.expander("🆕 Create New Dataset", expanded=True):
            new_ds_name = st.text_input("Dataset Name", placeholder="e.g., High Value Transactions")
            new_ds_desc = st.text_area("Description (optional)", placeholder="Focus area, criteria, etc.")
            
            clone_option = st.checkbox("📋 Clone from existing dataset")
            clone_from = None
            if clone_option and all_datasets:
                clone_options = {ds['name']: ds['id'] for ds in all_datasets}
                clone_display = st.selectbox("Clone from", list(clone_options.keys()))
                clone_from = clone_options[clone_display]
            
            col_create1, col_create2 = st.columns(2)
            with col_create1:
                if st.button("✅ Create", type="primary", use_container_width=True):
                    if new_ds_name:
                        try:
                            new_id = dataset_mgr.create_dataset(
                                name=new_ds_name,
                                description=new_ds_desc,
                                clone_from=clone_from
                            )
                            st.success(f"✅ Created: {new_ds_name}")
                            dataset_mgr.set_active_dataset(new_id)
                            st.session_state['show_create_dataset'] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.error("Please provide a dataset name")
            
            with col_create2:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_new_ds"):
                    st.session_state['show_create_dataset'] = False
                    st.rerun()
    
    st.markdown("---")
    
    history_path = "data/ml/scoring_history.csv"
    if not os.path.exists(history_path):
        st.warning("⚠️ No scoring history found! Score some transactions in **ML Workflow → Tab 3** first.")
        st.stop()
    
    try:
        hist_df = pd.read_csv(history_path, on_bad_lines='warn')
        if hist_df.empty:
            st.warning("Scoring history is empty. Go score some transactions first!")
            st.stop()
            
        if 'fraud_probability' in hist_df.columns:
            hist_df = hist_df.dropna(subset=['fraud_probability'])
        
        st.success(f"✅ Loaded {len(hist_df):,} scored transactions")
    except Exception as e:
        st.error(f"Error loading history: {e}")
        st.stop()
    
    if 'review_queue' not in st.session_state:
        st.session_state.review_queue = []
    if 'queue_index' not in st.session_state:
        st.session_state.queue_index = 0
    if 'batch_edits' not in st.session_state:
        st.session_state.batch_edits = {}

    def detect_fraud_category(row):
        prob = row.get('fraud_probability', 0)
        amount = row.get('Transaction_Amount', 0)
        account_age = row.get('Account_Age', 0)
        prev_fraud = row.get('Previous_Fraudulent_Transactions', 0)
        if prob < 0.3: return "Not Fraud"
        elif prev_fraud > 0: return "Account Takeover"
        elif account_age < 30 and amount > 10000: return "Identity Theft"
        elif amount > 5000: return "Card Not Present"
        else: return "Other"
    
    st.subheader("1.1 Batch Selection")
    col_batch1, col_batch2, col_batch3 = st.columns([2, 1, 1])
    
    with col_batch1:
        batch_method = st.selectbox(
            "🎯 Sampling Strategy",
            ["Stratified (Balanced Risk Levels)", "Random (Unbiased)", "Uncertainty (Model Confused)", "Diverse (Max Feature Coverage)", "Edge Cases (Extremes)"],
            key="batch_method"
        )
    
    with col_batch2:
        batch_size = st.number_input("Batch Size", 5, 50, 20, step=5, key="batch_size")
    
    with col_batch3:
        if st.button("📦 Add Batch", type="primary", use_container_width=True):
            import numpy as np
            st.session_state.batch_edits = {}
            st.session_state.queue_index = 0
            method_key = batch_method.split("(")[0].strip()
            
            if method_key == "Random":
                sample_indices = np.random.choice(len(hist_df), size=min(batch_size, len(hist_df)), replace=False)
                batch = hist_df.iloc[sample_indices]
            elif method_key == "Stratified":
                if 'fraud_probability' in hist_df.columns:
                    low = hist_df[hist_df['fraud_probability'] < 0.3]
                    med = hist_df[(hist_df['fraud_probability'] >= 0.3) & (hist_df['fraud_probability'] <= 0.7)]
                    high = hist_df[hist_df['fraud_probability'] > 0.7]
                    n_low = min(len(low), batch_size // 3)
                    n_med = min(len(med), batch_size // 3)
                    n_high = min(len(high), batch_size // 3)
                    samples = []
                    if n_low > 0: samples.append(low.sample(n=n_low))
                    if n_med > 0: samples.append(med.sample(n=n_med))
                    if n_high > 0: samples.append(high.sample(n=n_high))
                    batch = pd.concat(samples) if samples else pd.DataFrame()
                    if len(batch) < batch_size:
                        remaining = batch_size - len(batch)
                        available = hist_df[~hist_df.index.isin(batch.index)] if len(batch) > 0 else hist_df
                        if len(available) >= remaining: batch = pd.concat([batch, available.sample(n=remaining)])
                        else: batch = pd.concat([batch, available])
                else: batch = hist_df.sample(n=min(batch_size, len(hist_df)))
            elif method_key == "Uncertainty":
                if 'fraud_probability' in hist_df.columns:
                    uncertain = hist_df[(hist_df['fraud_probability'] > 0.35) & (hist_df['fraud_probability'] < 0.65)]
                    batch = uncertain.sample(n=min(batch_size, len(uncertain))) if len(uncertain) > 0 else hist_df.sample(n=min(batch_size, len(hist_df)))
                else: batch = hist_df.sample(n=min(batch_size, len(hist_df)))
            elif method_key == "Diverse":
                if 'Transaction_Amount' in hist_df.columns:
                    sorted_df = hist_df.sort_values('Transaction_Amount')
                    indices = np.linspace(0, len(sorted_df)-1, min(batch_size, len(sorted_df)), dtype=int)
                    batch = sorted_df.iloc[indices]
                else: batch = hist_df.sample(n=min(batch_size, len(hist_df)))
            elif method_key == "Edge Cases":
                if 'fraud_probability' in hist_df.columns:
                    extremes = hist_df[(hist_df['fraud_probability'] < 0.05) | (hist_df['fraud_probability'] > 0.95)]
                    batch = extremes.sample(n=min(batch_size, len(extremes))) if len(extremes) > 0 else hist_df.sample(n=min(batch_size, len(hist_df)))
                else: batch = hist_df.sample(n=min(batch_size, len(hist_df)))
            
            st.session_state.review_queue = batch.to_dict('records')
            st.session_state.queue_index = 0
            st.session_state.batch_edits = {}
            st.session_state.batch_method_used = batch_method
            st.success(f"✅ Added {len(batch)} samples using {method_key} strategy!")
            st.rerun()
    
    if st.session_state.review_queue:
        queue_len = len(st.session_state.review_queue)
        current_pos = st.session_state.queue_index + 1
        st.markdown("---")
        st.subheader(f"📋 Review Queue: Sample {current_pos}/{queue_len}")
        st.caption(f"Method: {st.session_state.get('batch_method_used', 'N/A')}")
        
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 2])
        with col_nav1:
            if st.button("⬅️ Previous", disabled=(st.session_state.queue_index == 0), use_container_width=True):
                st.session_state.queue_index -= 1
                st.rerun()
        with col_nav2:
            if st.button("➡️ Next", disabled=(st.session_state.queue_index >= queue_len - 1), use_container_width=True):
                st.session_state.queue_index += 1
                st.rerun()
        with col_nav3:
            if st.button("🔄 Clear Queue", use_container_width=True):
                st.session_state.review_queue = []
                st.session_state.queue_index = 0
                st.rerun()
        with col_nav4:
            st.progress((current_pos) / queue_len)
        
        selected_row = pd.Series(st.session_state.review_queue[st.session_state.queue_index])
    else:
        st.markdown("---")
        st.info("💡 **No batch selected.** Use manual selection below, or click 'Add Batch' above.")
        st.subheader("1.1B 🔍 Manual Selection")
        search_query = st.text_input("🔍 Search by Transaction ID (supports wildcards: * and ?)", placeholder="e.g., T15*, *001, T?5??", key="txn_search")
        
        filtered_df = hist_df.copy()
        if search_query:
            id_cols = [c for c in hist_df.columns if 'id' in c.lower() and 'fraud' not in c.lower()]
            if id_cols:
                import re
                id_col = id_cols[0]
                pattern = re.escape(search_query)
                pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
                pattern = f'^{pattern}$'
                try:
                    filtered_df = hist_df[hist_df[id_col].astype(str).str.match(pattern, case=False, na=False)]
                    if filtered_df.empty:
                        st.warning(f"No transactions found matching '{search_query}'")
                        filtered_df = hist_df
                except:
                    filtered_df = hist_df
        
        col_sel1, col_sel2 = st.columns([3, 1])
        with col_sel1:
            if len(filtered_df) > 0:
                filtered_df['display'] = filtered_df.apply(
                    lambda row: f"Prob: {row.get('fraud_probability', 0):.2%} | Amount: {row.get('Transaction_Amount', 'N/A')} | Time: {row.get('timestamp', 'N/A')}"[:50], axis=1
                )
                selected_idx = st.selectbox(
                    f"Choose a transaction ({len(filtered_df):,} available)",
                    options=range(len(filtered_df)),
                    format_func=lambda i: f"#{i+1}: {filtered_df.iloc[i]['display']}",
                    key="select_transaction"
                )
                selected_row = filtered_df.iloc[selected_idx]
        with col_sel2:
            st.metric("Fraud Probability", f"{selected_row.get('fraud_probability', 0):.1%}")
    
    st.markdown("---")
    st.subheader("1.2 🤖 AI Quick Recommendation")
    
    prob = selected_row.get('fraud_probability', 0)
    amount = selected_row.get('Transaction_Amount', 0)
    account_age = selected_row.get('Account_Age', 0)
    prev_fraud = selected_row.get('Previous_Fraudulent_Transactions', 0)
    num_txns_24h = selected_row.get('Number_of_Transactions_Last_24H', 0)
    
    votes = {"fraud": 0, "not_fraud": 0, "uncertain": 0}
    if prob > 0.7: votes["fraud"] += 1
    elif prob < 0.3: votes["not_fraud"] += 1
    else: votes["uncertain"] += 1
    
    if prev_fraud > 0: votes["fraud"] += 1
    else: votes["not_fraud"] += 1
    
    if account_age < 30 and amount > 5000: votes["fraud"] += 1
    elif account_age > 90: votes["not_fraud"] += 1
    else: votes["uncertain"] += 1
    
    if num_txns_24h > 10: votes["fraud"] += 1
    elif num_txns_24h <= 3: votes["not_fraud"] += 1
    else: votes["uncertain"] += 1
    
    total_votes = sum(votes.values())
    fraud_pct = votes["fraud"] / total_votes
    ai_category = detect_fraud_category(selected_row)
    
    if max(votes.values()) >= 3: confidence, confidence_color = "High", "🟢"
    elif max(votes.values()) == 2: confidence, confidence_color = "Medium", "🟡"
    else: confidence, confidence_color = "Low", "🔴"
    
    if votes["fraud"] >= 3: action, risk_level, risk_emoji = "Block & Investigate", "HIGH RISK", "🛑"
    elif votes["fraud"] >= 2: action, risk_level, risk_emoji = "Review Required", "MODERATE RISK", "⚠️"
    elif votes["not_fraud"] >= 3: action, risk_level, risk_emoji = "Approve", "LOW RISK", "✅"
    else: action, risk_level, risk_emoji = "Manual Review", "UNCERTAIN", "❓"
    
    col_card1, col_card2, col_card3, col_card4 = st.columns(4)
    with col_card1: st.metric("Category", ai_category, help="AI-detected fraud pattern")
    with col_card2: st.metric("Confidence", f"{confidence_color} {confidence}", delta=f"{fraud_pct:.0%} fraud votes", help=f"Ensemble: {votes['fraud']}/4 fraud, {votes['not_fraud']}/4 safe, {votes['uncertain']}/4 uncertain")
    with col_card3: st.metric("Recommended Action", action, help="Based on ensemble consensus")
    with col_card4: st.metric("Risk Level", f"{risk_emoji} {risk_level}", help=f"Probability: {prob:.1%}")
    
    st.markdown("---")
    st.subheader("1.3 Transaction Details")
    feature_cols = [c for c in selected_row.index if c not in ['display', 'timestamp', 'fraud_probability']]
    if feature_cols:
        col_det1, col_det2 = st.columns(2)
        mid_point = len(feature_cols) // 2
        with col_det1:
            for col in feature_cols[:mid_point]: st.text(f"{col}: {selected_row[col]}")
        with col_det2:
            for col in feature_cols[mid_point:]: st.text(f"{col}: {selected_row[col]}")
    
    st.markdown("---")
    with st.expander("📊 ML Confidence Metrics", expanded=False):
        st.caption("**Data-driven insights for confident decision-making**")
        st.markdown("### 🎯 Feature Importance")
        feature_impacts = []
        if prev_fraud > 0: feature_impacts.append(("Previous Fraud History", prev_fraud * 15, "🔴"))
        if num_txns_24h > 5: feature_impacts.append(("Transaction Velocity", (num_txns_24h - 5) * 3, "🔴" if num_txns_24h > 10 else "🟡"))
        if account_age < 30: feature_impacts.append(("Account Age (New)", (30 - account_age) * 0.5, "🔴"))
        elif account_age > 90: feature_impacts.append(("Account Age (Established)", (account_age - 90) * -0.2, "🟢"))
        if amount > 5000: feature_impacts.append(("High Amount", (amount - 5000) / 100, "🔴"))
        if prob > 0.5: feature_impacts.append(("Model Probability", prob * 50, "🔴"))
        elif prob < 0.3: feature_impacts.append(("Model Probability", (0.3 - prob) * -50, "🟢"))
        
        if feature_impacts:
            feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
            for feature, impact, emoji in feature_impacts[:5]:
                direction = "increases" if impact > 0 else "decreases"
                st.markdown(f"{emoji} **{feature}:** {direction} fraud likelihood by ~{abs(impact):.1f} points")
        else:
            st.info("No significant feature impacts")
        
        st.markdown("---")
        st.markdown("### 🔍 Similar Historical Cases")
        similar_txns = hist_df[(hist_df['Transaction_Amount'].between(amount * 0.8, amount * 1.2)) & (hist_df['Account_Age'].between(account_age - 30, account_age + 30))]
        if len(similar_txns) > 1 and 'Fraudulent' in similar_txns.columns:
            fraud_count = similar_txns['Fraudulent'].sum()
            total_count = len(similar_txns)
            fraud_rate = fraud_count / total_count
            st.markdown(f"**Found {total_count} similar:** {fraud_count} fraud ({fraud_rate:.0%}), {total_count - fraud_count} legitimate")
            if fraud_rate > 0.7: st.error(f"⚠️ HIGH RISK: {fraud_rate:.0%} of similar cases were fraud")
            elif fraud_rate > 0.4: st.warning(f"⚠️ MODERATE: {fraud_rate:.0%} of similar cases were fraud")
            else: st.success(f"✅ LOW RISK: Only {fraud_rate:.0%} fraud")
        else:
            st.info("Not enough similar transactions")
        
        st.markdown("---")
        st.markdown("### 🎲 Model Calibration")
        if prob > 0.7: st.markdown(f"**Predicted:** {prob:.1%} | **Confidence:** HIGH (80-90% accurate)")
        elif prob > 0.3: st.markdown(f"**Predicted:** {prob:.1%} | **Confidence:** MEDIUM (use judgment)")
        else: st.markdown(f"**Predicted:** {prob:.1%} | **Confidence:** HIGH (85-95% accurate)")
    
    st.markdown("---")
    st.subheader("1.4 AI Fraud Analysis")
    with st.expander("📖 View Detailed Fraud Analysis", expanded=True):
        explanation = f"""## Fraud Risk Analysis Report\n**Overall Assessment:** {risk_level} (Confidence: {confidence})\n### 🔍 Key Indicators\n**Red Flags:**\n"""
        red_flags = []
        if amount > 5000: red_flags.append(f"• High transaction amount: ${amount:,.2f}")
        if prev_fraud > 0: red_flags.append(f"• ⚠️ **CRITICAL:** Account has {prev_fraud} previous fraudulent transaction(s)")
        if num_txns_24h > 10: red_flags.append(f"• ⚠️ **High velocity:** {num_txns_24h} transactions in 24 hours (possible automated attack)")
        if account_age < 30: red_flags.append(f"• New account: Only {account_age} days old")
        if prob > 0.5 and amount < 100: red_flags.append(f"• Testing pattern: Small amount with high fraud probability")
        if red_flags: explanation += "\n".join(red_flags) + "\n"
        else: explanation += "• None detected\n"
        
        explanation += """\n**Green Flags (Legitimacy Indicators):**\n"""
        green_flags = []
        if account_age > 90: green_flags.append(f"• Established account: {account_age} days reduces baseline risk")
        if num_txns_24h <= 3: green_flags.append(f"• Normal velocity: {num_txns_24h} transactions/24h")
        if prob < 0.3: green_flags.append(f"• Low model probability: {prob:.1%}")
        if prev_fraud == 0: green_flags.append("• Clean history: No previous fraud")
        if green_flags: explanation += "\n".join(green_flags) + "\n"
        else: explanation += "• Limited positive indicators\n"
        
        explanation += f"\n### 💡 Decision Guidance\n**Recommended Action:** {action}\n"
        if votes["fraud"] >= 3:
            explanation += "**Investigation Priority:** HIGH\n- Immediate actions: Block transaction pending investigation.\n"
        elif votes["fraud"] >= 2:
            explanation += "**Investigation Priority:** MEDIUM\n- Immediate actions: Hold transaction for 30-60 minutes, send step-up auth.\n"
        elif votes["not_fraud"] >= 3:
            explanation += "**Investigation Priority:** LOW\n- Recommend: Approve.\n"
        else:
            explanation += "**Investigation Priority:** UNCERTAIN\n- Recommend: Manual review of typical patterns.\n"
            
        if prev_fraud > 0: explanation += f"\n### ⚠️ **SPECIAL NOTE: Previous Fraud**\nThis account has {prev_fraud} previous fraudulent transactions.\n"
        if num_txns_24h > 10: explanation += f"\n### 🚨 **VELOCITY ALERT**\n{num_txns_24h} transactions in 24 hours.\n"
        
        explanation += f"\n### 📊 Model Probability: {prob:.1%}\n"
        st.markdown(explanation)
    
    st.markdown("---")
    st.subheader("1.5 Your Expert Feedback")
    expert_correction = st.text_area("Provide your expert analysis", placeholder="Explain why this is or isn't fraud...", height=150, key="expert_correction")
    col_rate1, col_rate2, col_rate3 = st.columns([2, 1, 1])
    with col_rate1:
        category = st.selectbox(f"Fraud Category (AI suggests: {ai_category})", ["Not Fraud", "Account Takeover", "Identity Theft", "Card Not Present", "Synthetic Identity", "Other"], index=0, key="fraud_category")
    with col_rate2:
        quality_rating = st.selectbox("AI Quality", ["Excellent", "Good", "Fair", "Poor"], index=1, key="quality_rating")
    with col_rate3:
        already_saved = st.session_state.review_queue and st.session_state.queue_index in st.session_state.batch_edits
        button_label = "💾 Update" if already_saved else "💾 Save Current"
        button_type = "primary" if already_saved else "secondary"
        if st.button(button_label, type=button_type, use_container_width=True):
            if already_saved: st.warning("⚠️ Updating existing save.")
            training_example = {
                "input": f"Transaction (Prob: {prob:.1%}, Amount: ${amount:,.2f})",
                "output": expert_correction,
                "category": category,
                "rating": quality_rating,
                "fraud_probability": float(prob),
                "timestamp": datetime.now().isoformat()
            }
            if st.session_state.review_queue:
                st.session_state.batch_edits[st.session_state.queue_index] = training_example
                st.success(f"✅ {'Updated' if already_saved else 'Added'} batch!")
            else:
                with open(DATASET_FILE, 'a') as f:
                    f.write(json.dumps(training_example) + '\n')
                new_count = "N/A"
                if active_dataset_id:
                    dataset_mgr.add_sample(active_dataset_id, training_example)
                    fresh_ds = dataset_mgr.get_dataset(active_dataset_id)
                    new_count = fresh_ds['sample_count']
                st.success(f"✅ Saved to dataset! (Total: {new_count})")
                import time; time.sleep(1); st.rerun()

    if st.session_state.review_queue:
        st.markdown("---")
        col_bs1, col_bs2 = st.columns([2, 1])
        with col_bs1:
            st.caption(f"📝 You've edited {len(st.session_state.batch_edits)}/{len(st.session_state.review_queue)} samples")
        with col_bs2:
            if st.button("💾 Save All Batch Edits", type="primary", use_container_width=True):
                if st.session_state.batch_edits:
                    with open(DATASET_FILE, 'a') as f:
                        for example in st.session_state.batch_edits.values(): f.write(json.dumps(example) + '\n')
                    if active_dataset_id:
                        for example in st.session_state.batch_edits.values(): dataset_mgr.add_sample(active_dataset_id, example)
                    st.success(f"✅ Saved {len(st.session_state.batch_edits)} samples!")
                    st.balloons()
                    st.session_state.batch_edits = {}
                    st.session_state.review_queue = []
                    st.session_state.queue_index = 0
                    st.rerun()
                else:
                    st.warning("No edits to save yet.")
                    
    dataset_to_track_name = "Global"
    current_count = 0
    if active_dataset_id:
        active_ds = dataset_mgr.get_dataset(active_dataset_id)
        if active_ds:
            dataset_to_track_name = active_ds['name']
            current_count = active_ds['sample_count']
    elif DATASET_FILE.exists():
        with open(DATASET_FILE, 'r') as f: current_count = sum(1 for _ in f)
        
    st.markdown("---")
    st.subheader(f"📈 Collection Progress ({dataset_to_track_name})")
    target = 100
    progress = min(current_count / target, 1.0)
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1: st.progress(progress)
    with col_prog2: st.metric("Examples", f"{current_count}/{target}")
    
    col_clean1, col_clean2 = st.columns([3, 1])
    with col_clean1: st.caption("🧹 Remove duplicate entries")
    with col_clean2:
        if st.button("🧹 Clean Dataset", use_container_width=True):
            if active_dataset_id:
                examples = dataset_mgr.get_samples(active_dataset_id)
                seen_inputs = {ex.get('input', ''): ex for ex in examples}
                unique_examples = list(seen_inputs.values())
                if len(examples) > len(unique_examples):
                    dataset_mgr._save_samples(active_dataset_id, unique_examples)
                    dataset_mgr._update_sample_count(active_dataset_id)
                    with open(DATASET_FILE, 'w') as f:
                        for example in unique_examples: f.write(json.dumps(example) + '\n')
                    st.success(f"✅ Cleaned! Removed {len(examples) - len(unique_examples)} duplicates.")
                    st.rerun()
                else: st.info("✨ Dataset already clean.")
            else:
                examples = []
                with open(DATASET_FILE, 'r') as f:
                    for line in f:
                        try: examples.append(json.loads(line))
                        except: continue
                seen_inputs = {ex.get('input', ''): ex for ex in examples}
                unique_examples = list(seen_inputs.values())
                if len(examples) > len(unique_examples):
                    with open(DATASET_FILE, 'w') as f:
                        for example in unique_examples: f.write(json.dumps(example) + '\n')
                    st.success(f"✅ Cleaned! Removed {len(examples) - len(unique_examples)} duplicates.")
                    st.rerun()
                else: st.info("✨ Dataset already clean.")
                
        if current_count >= target: st.success("🎉 You've reached 100 examples! Ready to fine-tune!")
        elif current_count >= 50: st.info(f"Great progress! {target - current_count} more examples recommended.")
        
    if current_count > 0 and active_dataset_id:
        _all_ex = dataset_mgr.get_samples(active_dataset_id)
        if _all_ex:
            import altair as _alt
            _ratings = pd.Series([e.get('rating', 'Unknown') for e in _all_ex]).value_counts().reset_index()
            _ratings.columns = ['Rating', 'Count']
            _color_map = {'Excellent': '#2ecc71', 'Good': '#3498db', 'Fair': '#f39c12', 'Poor': '#e74c3c', 'Unknown': '#95a5a6'}
            _ratings['Color'] = _ratings['Rating'].map(_color_map).fillna('#95a5a6')
            st.markdown("#### 🎯 Quality Breakdown")
            _qchart = _alt.Chart(_ratings).mark_bar().encode(
                x=_alt.X('Count:Q', title='Samples'),
                y=_alt.Y('Rating:N', sort=None, title=''),
                color=_alt.Color('Color:N', scale=None, legend=None),
                tooltip=['Rating', 'Count']
            ).properties(height=120)
            st.altair_chart(_qchart, use_container_width=True)
            _good_pct = _ratings[_ratings['Rating'].isin(['Excellent', 'Good'])]['Count'].sum() / current_count
            st.caption(f"{_good_pct:.0%} of samples rated Excellent/Good — quality threshold for fine-tuning is ≥70%")
