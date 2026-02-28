import streamlit as st
import pandas as pd
import altair as alt
from agents.llm_router import init_llm
from ml.auto_trainer import train_models
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

def render_train_tab(can_control):
    st.header("Step 2: Auto-Train Fraud Models")
    st.info("Train baseline models (Logistic Regression & Random Forest) using the dataset created in Step 1.")

    custom_output_dir = st.text_input(
        "Server Save Directory:", 
        value="data/models",
        help="Where models will be saved.",
        key="train_output_dir"
    )

    use_optimization = st.checkbox("✨ Enable Hyperparameter Optimization (Slower but accurate)", value=False, key="train_optimize_flags")

    custom_config = None
    if not use_optimization:
        with st.expander("⚙️ Advanced Model Configuration", expanded=False):
            st.caption("Manual override for model parameters. Ignored if Optimization is enabled.")
            
            st.markdown("**Random Forest**")
            c1, c2 = st.columns(2)
            rf_n = c1.slider("RF Trees (n_estimators)", 10, 500, 100, 10, key="rf_n")
            rf_d = c2.selectbox("RF Max Depth", [None, 5, 10, 20, 50], index=2, key="rf_d")
            
            st.markdown("**Gradient Boosting**")
            c3, c4 = st.columns(2)
            gb_n = c3.slider("GBM Trees", 10, 500, 100, 10, key="gb_n")
            gb_lr = c4.number_input("Learning Rate", 0.01, 1.0, 0.1, 0.01, key="gb_lr")
            
            st.markdown("**Logistic Regression**")
            lr_c = st.select_slider("Regularization Strength (C)", options=[0.01, 0.1, 1.0, 10.0, 100.0], value=1.0, key="lr_c")
            
            custom_config = {
                "random_forest": {"n_estimators": rf_n, "max_depth": rf_d},
                "gradient_boosting": {"n_estimators": gb_n, "learning_rate": gb_lr},
                "logistic_regression": {"C": lr_c}
            }

    if can_control:
        train_start_btn = st.button("🚀 Train Models Now", key="train_start")
    else:
        st.button("🚀 Train Models Now", key="train_start", disabled=True, help="Admin access required")
        train_start_btn = False

    if train_start_btn:
        try:
            if "tasks" not in st.session_state: st.session_state.tasks = []
            task_id = f"train_{int(pd.Timestamp.now().timestamp())}"
            st.session_state.tasks.append({
                "id": task_id,
                "name": "Auto-Training Models",
                "status": "running",
                "progress": 0.2,
                "timestamp": pd.Timestamp.now().strftime("%H:%M:%S")
            })
            
            with st.spinner("Training models (Analysis & Tuning)..."):
                result = train_models(
                    train_path="data/ml/train.csv",
                    val_path="data/ml/validation.csv",
                    test_path="data/ml/test.csv",
                    features_path="data/ml/features.json",
                    output_dir=custom_output_dir,
                    optimize_hyperparameters=use_optimization,
                    custom_config=custom_config
                )
                st.session_state.auto_train_result = result
                st.success(f"Training complete! Best model: {result['best_model_name']}")
                st.session_state.last_trained_model_path = result['saved_model_path']
                
                for t in st.session_state.tasks:
                    if t["id"] == task_id:
                        t["status"] = "completed"
                        t["progress"] = 1.0
                
        except Exception as e:
            st.error(f"Auto-training failed: {e}")

    if "auto_train_result" in st.session_state:
        res = st.session_state.auto_train_result
        st.subheader("📊 Model Comparison")

        metrics_dict = res.get("metrics", {})
        if metrics_dict:
            rows = []
            for model_name, m in metrics_dict.items():
                rows.append({
                    "Model": model_name,
                    "Accuracy": f"{m.get('accuracy', 0):.1%}",
                    "F1 (weighted)": f"{m.get('f1', 0):.3f}",
                    "Precision": f"{m.get('precision', 0):.3f}",
                    "Recall": f"{m.get('recall', 0):.3f}",
                    "🏆 Best?": "✅" if model_name == res.get('best_model_name') else "",
                })
            cmp_df = pd.DataFrame(rows)
            st.dataframe(cmp_df, use_container_width=True, hide_index=True)
        else:
            st.json(metrics_dict) 
        
        if st.button("🤖 Analyze Performance", key="train_analyze"):
            with st.spinner("Analyzing..."):
                llm = init_llm(st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini"))
                prompt = f"Analyze these fraud detection metrics:\n{res['metrics']}\n\nCompare RF vs LR."
                st.session_state.train_analysis = llm.invoke(prompt).content
        
        if "train_analysis" in st.session_state:
            st.info(st.session_state.train_analysis)

        st.markdown("---")
        st.subheader("🎚️ Dynamic Sensitivity Tuning")
        st.caption("Adjust the decision threshold to balance Precision vs Recall (e.g., lower threshold = catch more fraud).")
        
        if "tuning_data" not in st.session_state or st.session_state.get("tuning_model_path") != res['saved_model_path']:
            try:
                import pickle
                with open(res['saved_model_path'], "rb") as f:
                    tuning_model = pickle.load(f)
                
                val_df = pd.read_csv("data/ml/validation.csv")
                if "label" in val_df.columns:
                    val_df = val_df.dropna(subset=["label"])
                    X_val = val_df.drop(columns=["label"])
                    y_val = val_df["label"]
                    
                    if hasattr(tuning_model, "predict_proba"):
                        y_proba = tuning_model.predict_proba(X_val)[:, 1]
                        
                        st.session_state.tuning_data = {
                            "y_val": y_val.values,
                            "y_proba": y_proba
                        }
                        st.session_state.tuning_model_path = res['saved_model_path']
                    else:
                        st.warning("Selected model does not support probability prediction.")
            except Exception as e:
                st.warning(f"Could not load data for tuning: {e}")

        if "tuning_data" in st.session_state:
            data = st.session_state.tuning_data
            y_val = data["y_val"]
            y_proba = data["y_proba"]
            
            st.caption("Model Confidence Distribution (Predicted Probabilities)")
            hist_df = pd.DataFrame({"Probability": y_proba})
            hist = alt.Chart(hist_df).mark_bar().encode(
                x=alt.X("Probability", bin=alt.Bin(maxbins=20), title="Fraud Probability"),
                y='count()',
                tooltip=['count()']
            ).properties(height=150)
            st.altair_chart(hist, use_container_width=True)
            
            with st.expander("ℹ️ How to read this Histogram", expanded=False):
                st.markdown("""
                - **X-Axis (Probability):** The model's confidence scores (0.0 to 1.0).
                - **Y-Axis (Count):** How many validation samples naturally fall into that confidence range.
                - **Interpretation:** 
                    - If bars are bunched at **0.0 and 1.0**, the model is very decisive.
                    - If bars are spread in the **middle (0.4-0.6)**, the model is uncertain, and moving the threshold will have a big impact.
                """)

            threshold = st.slider("Target Probability Threshold", 0.0, 1.0, 0.5, 0.01)
            
            y_pred_new = (y_proba >= threshold).astype(int)
            
            from sklearn.metrics import precision_score, recall_score
            acc = accuracy_score(y_val, y_pred_new)
            f1 = f1_score(y_val, y_pred_new, average='weighted')
            prec = precision_score(y_val, y_pred_new, zero_division=0)
            rec = recall_score(y_val, y_pred_new, zero_division=0)
            cm = confusion_matrix(y_val, y_pred_new)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precision", f"{prec:.2f}", help="Accuracy of positive predictions")
            c2.metric("Recall", f"{rec:.2f}", help="Fraction of actual fraud detected")
            c3.metric("F1 Score", f"{f1:.2f}")
            c4.metric("Accuracy", f"{acc:.1%}")
            
            cm_data = []
            for i, actual in enumerate(["Normal", "Fraud"]):
                for j, pred in enumerate(["Normal", "Fraud"]):
                    cm_data.append({"Actual": actual, "Predicted": pred, "Count": cm[i][j]})
            cm_source = pd.DataFrame(cm_data)

            base = alt.Chart(cm_source).encode(
                x=alt.X('Predicted', title='Predicted Label'),
                y=alt.Y('Actual', title='Actual Label')
            )
            heatmap = base.mark_rect().encode(
                color=alt.Color('Count', legend=None)
            )
            text = base.mark_text().encode(
                text='Count',
                color=alt.value('white')
            )
            st.altair_chart(heatmap + text, use_container_width=True)
            
            with st.expander("ℹ️ How to read these Metrics", expanded=False):
                st.markdown("""
                **Confusion Matrix (The Heatmap):**
                - **Top-Left (True Negative):** Normal transactions correctly flagged as Normal. (Good)
                - **Bottom-Right (True Positive):** Fraud correctly caught. (Good)
                - **Top-Right (False Positive):** Normal flagged as Fraud. (Annoying for users)
                - **Bottom-Left (False Negative):** Fraud missed. (Dangerous!)
                
                **Trade-off:**
                - **Higher Threshold (>0.5):** Stricter. Fewer False Positives, but might miss fraud (Lower Recall).
                - **Lower Threshold (<0.5):** Sensitive. Catches more fraud (High Recall), but flags more innocent people (Lower Precision).
                """)
