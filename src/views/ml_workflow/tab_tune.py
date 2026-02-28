import streamlit as st
import pandas as pd
import os
from ml.auto_trainer import train_models

def render_tune_tab(can_control):
    st.header("Step 4: Continuous Learning (Fine-Tuning)")
    st.info("Improve the model by correcting mistakes from Live Scoring history.")

    with st.expander("ℹ️ What is 'fraud_risk_score' and 'verified_label'?", expanded=False):
        st.markdown("""
        - **Fraud Risk Score (0.0 - 1.0):** This is the probability calculated by the model.
            - `0.00` = Definitely Safe
            - `1.00` = Definitely Fraud
            - `> 0.50` = Usually flagged as Fraud by default.
        - **Verified Label (0 or 1):** This is the **True Correct Answer**.
            - `0` = Normal Transaction
            - `1` = Actual Fraud
        
        **Why correcting matters:**
        If the model says **Risk = 0.95** (High Risk) but you know it was actually **Safe (Label 0)**, marking it here and re-training teaches the model not to make that mistake again!
        """)

    history_path = "data/ml/scoring_history.csv"
    train_path = "data/ml/train.csv"

    if not os.path.exists(history_path):
        st.warning("No scoring history found yet. Go to 'Live Scoring' and make some predictions!")
    else:
        with st.expander("🛠️ Troubleshooting", expanded=False):
            st.caption("If you see CSV errors, the history file may be corrupted from schema changes.")
            if can_control:
                del_btn = st.button("🗑️ Delete History & Start Fresh", type="secondary")
            else:
                st.button("🗑️ Delete History & Start Fresh", type="secondary", disabled=True, help="Admin access required")
                del_btn = False

            if del_btn:
                try:
                    os.remove(history_path)
                    st.success("History deleted! Refresh the page.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")
        try:
            hist_df = pd.read_csv(history_path, on_bad_lines='warn')
            original_count = len(hist_df)
            
            if hist_df.empty:
                st.error("📁 Scoring history file is empty or corrupted. Delete `data/ml/scoring_history.csv` to start fresh.")
                st.stop()
            
            id_candidates = [c for c in hist_df.columns if 'id' in c.lower() and 'fraud' not in c.lower()]
            
            if id_candidates and 'timestamp' in hist_df.columns:
                id_col = id_candidates[0]
                hist_df = hist_df.sort_values('timestamp', ascending=False)
                hist_df = hist_df.drop_duplicates(subset=[id_col], keep='first')
                dedup_method = f"ID ({id_col})"
            elif 'timestamp' in hist_df.columns:
                feature_cols = [c for c in hist_df.columns if c not in ['timestamp', 'fraud_probability']]
                if feature_cols:
                    hist_df = hist_df.sort_values('timestamp', ascending=False)
                    hist_df = hist_df.drop_duplicates(subset=feature_cols, keep='first')
                    dedup_method = "Feature Match"
                else:
                    dedup_method = "None (No Features)"
            else:
                dedup_method = "None (No Timestamp)"
            
            dupes_removed = original_count - len(hist_df)
            if dupes_removed > 0:
                st.info(f"🧹 Removed {dupes_removed} duplicate scoring event(s) via {dedup_method}. Showing {len(hist_df)} unique transactions.")
            
            st.subheader("4.1 Review Recent Predictions")
            st.caption("Select rows that were predicted incorrectly, correct the label, and add them to the training set.")
            
            c_sort1, c_sort2 = st.columns([2, 1])
            with c_sort1:
                sort_col = st.selectbox(
                    "Sort Table By", 
                    options=hist_df.columns.tolist(), 
                    index=hist_df.columns.tolist().index("timestamp") if "timestamp" in hist_df.columns else 0,
                    key="tune_sort_col"
                )
            with c_sort2:
                sort_asc = st.radio("Order", ["Descending", "Ascending"], index=0, horizontal=True, key="tune_sort_asc")
            
            ascending = (sort_asc == "Ascending")
            hist_df = hist_df.sort_values(sort_col, ascending=ascending)
            
            hist_df["ai_suggestion"] = False
            if "fraud_probability" in hist_df.columns:
                if len(hist_df) > 0:
                    min_prob = hist_df["fraud_probability"].min()
                    max_prob = hist_df["fraud_probability"].max()
                    mean_prob = hist_df["fraud_probability"].mean()
                    st.caption(f"📊 Probability Range: {min_prob:.3f} - {max_prob:.3f} (avg: {mean_prob:.3f})")
                
                mask_uncertain = (hist_df["fraud_probability"] > 0.35) & (hist_df["fraud_probability"] < 0.65)
                mask_high = (hist_df["fraud_probability"] > 0.90)
                mask_low = (hist_df["fraud_probability"] < 0.10)
                
                hist_df.loc[mask_uncertain | mask_high | mask_low, "ai_suggestion"] = True

            n_recs = int(hist_df["ai_suggestion"].sum()) if "ai_suggestion" in hist_df.columns else 0
            
            if n_recs == 0:
                st.caption("💡 No AI recommendations found. The model appears confident about all predictions. You can still manually select rows to verify.")
            else:
                st.caption(f"🤖 AI found {n_recs} interesting cases: uncertain predictions, extreme risks, or possible false negatives.")
            if st.button(f"✨ Auto-Select {n_recs} AI Recommendations", disabled=(n_recs==0)):
                hist_df["add_to_train"] = hist_df["ai_suggestion"]
                st.toast(f"Selected {n_recs} rows!")
                
                if "tune_editor_key" not in st.session_state:
                    st.session_state.tune_editor_key = 0
                st.session_state.tune_editor_key += 1
                st.rerun()

            if "tune_editor_key" not in st.session_state:
                st.session_state.tune_editor_key = 0
            
            if "verified_label" not in hist_df.columns:
                if "fraud_probability" in hist_df.columns:
                    hist_df.insert(0, "verified_label", (hist_df["fraud_probability"] > 0.5).astype(int))
                else:
                    hist_df.insert(0, "verified_label", 0)

            if "add_to_train" not in hist_df.columns:
                hist_df.insert(0, "add_to_train", False)

            edited_df = st.data_editor(
                hist_df,
                key=f"tune_editor_{st.session_state.tune_editor_key}",
                num_rows="dynamic",
                column_config={
                    "add_to_train": st.column_config.CheckboxColumn(
                        "✅ Add to Training?",
                        help="Check this to include this row in the next training cycle.",
                        default=False,
                    ),
                    "ai_suggestion": st.column_config.CheckboxColumn(
                        "💡 AI Recommended",
                        help="AI wants you to review this because it is Uncertain relative to 0.5 or Very High Risk.",
                        disabled=True, 
                    ),
                    "verified_label": st.column_config.CheckboxColumn(
                        "Is Fraud? (Corrected)",
                        help="Check if this is ACTUAL Fraud. Uncheck if Normal.",
                        default=False,
                    ),
                    "fraud_probability": st.column_config.ProgressColumn(
                        "Predicted Risk",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    "timestamp": st.column_config.DatetimeColumn("Scored At", format="D MMM, HH:mm"),
                },
                disabled=[c for c in hist_df.columns if c not in ["verified_label", "add_to_train"]]
            )

            st.subheader("4.2 Re-Train Model")
            
            num_selected = edited_df["add_to_train"].sum()
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button(f"📥 Add {num_selected} Selected Rows to Training", key="tune_add_btn", disabled=(num_selected==0)):
                    try:
                        if os.path.exists(train_path):
                            train_df = pd.read_csv(train_path)
                            
                            rows_to_add = edited_df[edited_df["add_to_train"]].copy()
                            if rows_to_add.empty:
                                st.warning("No rows selected! Check the '✅ Add to Training?' box first.")
                            else:
                                rows_to_add["label"] = rows_to_add["verified_label"]
                                
                                common_cols = list(set(train_df.columns) & set(rows_to_add.columns))
                                if not common_cols:
                                    st.error("No common columns found between history and training data!")
                                else:
                                    rows_to_add = rows_to_add[common_cols]
                                    
                                    updated_train_df = pd.concat([train_df, rows_to_add], ignore_index=True)
                                    updated_train_df.to_csv(train_path, index=False)
                                    st.success(f"Added {len(rows_to_add)} rows to Training Data! (Total: {len(updated_train_df)})")
                        else:
                            st.error("Original Training Data not found.")
                    except Exception as e:
                        st.error(f"Failed to add data: {e}")

            with col_t2:
                st.caption("Once data is added, re-run the Auto-Trainer to update the model.")
                if st.button("🔄 Retrain Now", key="tune_retrain_btn"):
                     try:
                        with st.spinner("Fine-tuning (Re-training)..."):
                            res = train_models(
                                train_path="data/ml/train.csv",
                                val_path="data/ml/validation.csv",
                                test_path="data/ml/test.csv",
                                features_path="data/ml/features.json",
                                output_dir="data/models",
                                optimize_hyperparameters=False 
                            )
                            st.session_state.auto_train_result = res
                            
                            best_name = res['best_model_name']
                            best_metrics = res['metrics'][best_name]
                            
                            st.success(f"✅ Fine-Tuning Complete! Best Model: **{best_name}**")
                            st.metric("Model F1 Score", f"{best_metrics.get('f1', 0):.3f}")
                            st.balloons()
                            
                            with st.expander("🎯 What's Next?", expanded=True):
                                st.markdown("""
                                Your model has been updated with the new verified data!
                                
                                **Recommended Next Steps:**
                                1. 🧪 **Test the Model**: Go to **Tab 3 → Live Scoring** to see if predictions improved
                                2. 📊 **Monitor Performance**: Keep an eye on fraud probability accuracy on real cases
                                3. 🔄 **Repeat the Cycle**: As you find more errors, return here to fine-tune again
                                
                                **Pro Tip**: The more edge cases you feed the model, the smarter it gets!
                                """)
                     except Exception as e:
                         st.error(f"Retrain failed: {e}")
                         
        except Exception as e:
            st.error(f"Error loading history: {e}")
