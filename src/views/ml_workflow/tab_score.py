import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import glob
import json
import shap
import matplotlib.pyplot as plt

from utils.data_manager import get_available_files
from agents.model_explanation_agent import explain_model_prediction
from ml.model_loader import load_model, load_features
from ml.live_preprocessing import prepare_live_data
from utils.schema_utils import build_schema_text_from_tables

def get_available_models(model_dir="data/models"):
    if not os.path.exists(model_dir): return []
    return glob.glob(os.path.join(model_dir, "*.pkl"))

def get_available_features(data_dir="data/ml"):
    if not os.path.exists(data_dir): return []
    return glob.glob(os.path.join(data_dir, "*.json"))

def check_drift(df, metadata_path="data/ml/metadata.json"):
    drifts = []
    if not os.path.exists(metadata_path): return []
    try:
        with open(metadata_path, "r") as f:
            meta = json.load(f)
            stats = meta.get("feature_stats", {})
        for col, stat in stats.items():
            if col in df.columns:
                val_max = df[col].max()
                val_min = df[col].min()
                train_max = stat['max']
                train_min = stat['min']
                if val_max > train_max * 1.5: 
                    drifts.append(f"⚠️ **{col}**: Value {val_max} is significantly higher than training max ({train_max})")
                elif val_min < train_min * 0.5 and train_min > 0:
                    drifts.append(f"⚠️ **{col}**: Value {val_min} is significantly lower than training min ({train_min})")
    except:
        pass
    return drifts

def explain_with_shap(model, X_df):
    try:
        clf = model["clf"] if "clf" in model.named_steps else model
        X_transformed = X_df.copy()
        if hasattr(model, "named_steps"):
            for step_name, step in model.named_steps.items():
                if step_name != "clf":
                    X_transformed = step.transform(X_transformed)
        try:
            explainer = shap.TreeExplainer(clf)
            shap_values = explainer(X_transformed)
        except Exception:
            bg_df = pd.read_csv("data/ml/train.csv", nrows=100)
            if "label" in bg_df.columns: bg_df = bg_df.drop(columns=["label"])
            bg_trans = bg_df.copy()
            if hasattr(model, "named_steps"):
                 for step_name, step in model.named_steps.items():
                    if step_name != "clf":
                        bg_trans = step.transform(bg_trans)
            explainer = shap.Explainer(clf, bg_trans)
            shap_values = explainer(X_transformed)
        fig, ax = plt.subplots(figsize=(8, 4))
        shap.plots.waterfall(shap_values[0], show=False)
        return fig
    except Exception as e:
        return f"SHAP Error: {e}"

def render_score_tab():
    st.header("Step 3: Real-Time Fraud Scoring")
    
    st.subheader("3.1 Select Configuration")
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        avail_models = get_available_models()
        if avail_models:
            idx = 0
            if "last_trained_model_path" in st.session_state:
                 try:
                     idx = avail_models.index(st.session_state.last_trained_model_path)
                 except: pass
            model_path = st.selectbox("Select Model:", avail_models, index=idx, key="score_model_select")
        else:
            st.warning("No models found.")
            model_path = None
            
    with col_m2:
        avail_feats = get_available_features()
        if avail_feats:
            features_path = st.selectbox("Select Features:", avail_feats, index=0, key="score_feat_select")
        else:
            features_path = st.text_input("Features path:", "data/ml/features.json", key="score_feat_manual")

    metadata_path = "data/ml/metadata.json"
    model = None
    feature_names = None

    if model_path and features_path:
        try:
            model = load_model(model_path)
            feature_names = load_features(features_path)
            st.success(f"Loaded: {os.path.basename(model_path)}")
        except Exception as e:
            st.error(f"Load Error: {e}")

    if model and feature_names:
        sub_tab_csv, sub_tab_manual = st.tabs(["📂 Batch Scoring (CSV)", "✍️ Manual Scoring"])
        
        with sub_tab_csv:
            st.subheader("Compute Fraud Scores")
            input_source = st.radio("Input Source:", ["🚀 Upload New CSV", "📂 Select Existing File"], horizontal=True, key="score_csv_source")
            
            df_input = None
            if input_source == "🚀 Upload New CSV":
                f = st.file_uploader("Upload CSV", type=["csv"], key="score_csv_upload")
                if f: df_input = pd.read_csv(f)
            else:
                files = [f for f in get_available_files() if f.lower().endswith('.csv')]
                sel_f = st.selectbox("Select File:", files, key="score_exist_select")
                if sel_f: df_input = pd.read_csv(os.path.join("data", "uploads", sel_f))
            
            if df_input is not None:
                st.dataframe(df_input.head(), height=150)
                
                drifts = check_drift(df_input)
                if drifts:
                    with st.expander("🚨 Data Drift Detected", expanded=True):
                        for d in drifts: st.markdown(d)
                        st.markdown("---")
                        st.markdown("""
                        **What to do:**
                        - ✅ **Option 1**: Continue scoring (model will handle minor drift)
                        - 🔄 **Option 2**: Go to **Tab 4 → Retrain** to update the model with this new data pattern
                        - 📊 **Option 3**: Go to **Tab 1** to rebuild the training dataset with recent data
                        """)

                if st.button("🚀 Score Data", key="score_csv_btn"):
                    try:
                        X_live, df_aug = prepare_live_data(df_input, metadata_path=metadata_path)
                        df_aug["fraud_probability"] = model.predict_proba(X_live)[:, 1]
                        
                        history_path = "data/ml/scoring_history.csv"
                        df_log = df_aug.copy()
                        df_log["timestamp"] = pd.Timestamp.now()
                        os.makedirs("data/ml", exist_ok=True)
                        if not os.path.exists(history_path):
                            df_log.to_csv(history_path, index=False)
                        else:
                            df_log.to_csv(history_path, mode='a', header=False, index=False)
                        
                        st.success("Scoring Complete & Logged!")
                        scored_df = df_aug.sort_values("fraud_probability", ascending=False)
                        st.dataframe(scored_df.head(50))

                        import io as _io
                        _sbuf = _io.StringIO()
                        scored_df.to_csv(_sbuf, index=False)
                        st.download_button(
                            label="⬇ Download Scored CSV",
                            data=_sbuf.getvalue(),
                            file_name="fraud_scored_results.csv",
                            mime="text/csv",
                            help="Download all rows with fraud_probability scores"
                        )

                        total = len(scored_df)
                        n_low = (scored_df["fraud_probability"] < 0.3).sum()
                        n_med = ((scored_df["fraud_probability"] >= 0.3) & (scored_df["fraud_probability"] < 0.7)).sum()
                        n_high = (scored_df["fraud_probability"] >= 0.7).sum()
                        st.markdown("**📊 Risk Distribution**")
                        g1, g2, g3 = st.columns(3)
                        g1.metric("🟢 Low Risk (< 30%)", n_low, f"{n_low/total:.0%}")
                        g2.metric("🟡 Medium Risk (30-70%)", n_med, f"{n_med/total:.0%}")
                        g3.metric("🔴 High Risk (> 70%)", n_high, f"{n_high/total:.0%}")

                        risk_df = pd.DataFrame({
                            "Band": ["🟢 Low", "🟡 Medium", "🔴 High"],
                            "Count": [n_low, n_med, n_high],
                            "Color": ["#2ecc71", "#f39c12", "#e74c3c"]
                        })
                        st.altair_chart(
                            alt.Chart(risk_df).mark_bar().encode(
                                x=alt.X("Band:N", sort=None, title="Risk Band"),
                                y=alt.Y("Count:Q", title="Number of Transactions"),
                                color=alt.Color("Color:N", scale=None, legend=None),
                                tooltip=["Band", "Count"]
                            ).properties(height=200, title="Fraud Risk Band Breakdown"),
                            use_container_width=True
                        )
                        
                        top_row = df_aug.sort_values("fraud_probability", ascending=False).iloc[0]
                        schema = build_schema_text_from_tables() if st.session_state.get('uploaded_tables') else "No schema."
                        
                        expl = explain_model_prediction(
                            top_row, top_row["fraud_probability"], 
                            model.__class__.__name__, "openai:gpt-4o-mini", schema
                        )
                        st.info(f"🧠 AI Analysis: {expl}")
                        
                        st.subheader("🕵️‍♂️ SHAP Explanation (Math-Based)")
                        with st.spinner("Calculating SHAP values..."):
                             try:
                                 X_live_df = pd.DataFrame(X_live, columns=feature_names)
                             except ValueError:
                                 X_live_df = pd.DataFrame(X_live)
                                 
                             shap_fig = explain_with_shap(model, X_live_df.iloc[[0]])
                             if isinstance(shap_fig, str):
                                 st.warning(shap_fig)
                             else:
                                 st.pyplot(shap_fig)
                                 plt.close(shap_fig)
                             
                             with st.expander("ℹ️ How to read this Waterfall Plot", expanded=False):
                                 st.markdown("""
                                 - **E[f(x)] (The Gray Line):** The average "baseline" risk of your dataset (e.g., 20%).
                                 - **Red Bars (+):** Features that pushed the risk **HIGHER** for this specific transaction.
                                 - **Blue Bars (-):** Features that pulled the risk **LOWER**.
                                 - **f(x) (Top Label):** The final calculated score for this transaction.
                                 """)

                    except Exception as e:
                        st.error(f"Scoring Failed: {e}")

        with sub_tab_manual:
            st.subheader("Manual Entry")
            
            c_mock, c_clear = st.columns(2)
            if c_mock.button("🤡 Mock Fraud Data"):
                st.session_state["manual_in_Transaction_Amount"] = "50000"
                st.session_state["manual_in_Time_of_Transaction"] = "15"
                st.session_state["manual_in_Previous_Fraudulent_Transactions"] = "0"
                st.session_state["manual_in_Account_Age"] = "90"
                st.session_state["manual_in_Number_of_Transactions_Last_24H"] = "1"
                st.rerun()
                
            if c_clear.button("🧹 Clear Entry"):
                for f in feature_names:
                    if f"manual_in_{f}" in st.session_state:
                         st.session_state[f"manual_in_{f}"] = ""
                st.rerun()

            manual_inputs = {}
            cols = st.columns(3)
            for i, c in enumerate(feature_names):
                with cols[i % 3]:
                    key_name = f"manual_in_{c}"
                    manual_inputs[c] = st.text_input(f"{c}:", key=key_name)
            
            if st.button("🎯 Score Manual Entry", key="score_manual_btn"):
                try:
                    df_s = pd.DataFrame([manual_inputs])
                    
                    drifts = check_drift(df_s)
                    if drifts:
                        for d in drifts: st.warning(d)
                        
                    X_l, df_a = prepare_live_data(df_s, metadata_path=metadata_path)
                    prob = model.predict_proba(X_l)[:, 1][0]
                    st.success(f"Fraud Probability: **{prob:.4f}**")
                    
                    history_path = "data/ml/scoring_history.csv"
                    log_entry = df_s.copy()
                    log_entry["fraud_probability"] = prob
                    log_entry["timestamp"] = pd.Timestamp.now()
                    
                    if not os.path.exists(history_path):
                        log_entry.to_csv(history_path, index=False)
                    else:
                        log_entry.to_csv(history_path, mode='a', header=False, index=False)
                    
                    st.subheader("🕵️‍♂️ SHAP Explanation")
                    with st.spinner("Calculating SHAP..."):
                        try:
                             X_l_df = pd.DataFrame(X_l, columns=feature_names)
                        except:
                             X_l_df = pd.DataFrame(X_l)
                             
                        shap_fig = explain_with_shap(model, X_l_df)
                        if isinstance(shap_fig, str):
                            st.warning(shap_fig)
                        else:
                            st.pyplot(shap_fig)
                            plt.close(shap_fig)
                            
                        with st.expander("ℹ️ How to read this Waterfall Plot", expanded=False):
                            st.markdown("""
                            - **E[f(x)] (The Gray Line):** The average "baseline" risk of your dataset (e.g., 20%).
                            - **Red Bars (+):** Features that pushed the risk **HIGHER** for this specific transaction.
                            - **Blue Bars (-):** Features that pulled the risk **LOWER**.
                            - **f(x) (Top Label):** The final calculated score for this transaction.
                            """)
                            
                except Exception as e:
                    st.error(f"Error: {e}")
