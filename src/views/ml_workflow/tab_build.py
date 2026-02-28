import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from utils.data_manager import get_available_tables, get_available_files, load_data
from agents.llm_router import init_llm
from ml.training_dataset_builder import build_training_dataset

def render_build_tab(can_control):
    st.header("Step 1: Build Training Dataset")
    
    st.subheader("1.1 Select Source Data")
    source_type = st.radio(
        "Source Type:", 
        ["SQL Tables", "Uploaded File", "Previous RAG Result"], 
        horizontal=True,
        key="build_source_type"
    )

    df_for_training = None

    if source_type == "Previous RAG Result":
        if st.session_state.get('best_df') is not None:
            df_for_training = st.session_state.best_df
            st.success("Loaded data from SQL RAG Assistant.")
        else:
            st.warning("No data found from previous RAG query. Please run a query on the SQL RAG page or select another source.")

    elif source_type == "SQL Tables":
        tables = get_available_tables()
        selected_tables = st.multiselect("Select Tables:", tables, key="build_sql_tables")
        if st.button("Load SQL Data", key="build_load_sql"):
            with st.spinner("Loading & Joining..."):
                data = load_data(source_type, selected_tables)
                if isinstance(data, pd.DataFrame):
                    st.session_state.train_df = data
                    st.rerun()

    elif source_type == "Uploaded File":
        files = get_available_files()
        f = st.selectbox("Choose File:", files, key="build_file_select")
        if st.button("Load File", key="build_load_file"):
            with st.spinner("Loading..."):
                data = load_data(source_type, [f] if f else [])
                if isinstance(data, pd.DataFrame):
                    st.session_state.train_df = data
                    st.rerun()

    if "train_df" in st.session_state and source_type != "Previous RAG Result":
        df_for_training = st.session_state.train_df

    if df_for_training is not None:
        st.markdown("---")
        st.subheader("1.2 Data Preview")
        st.markdown(f"**Loaded Data:** {len(df_for_training)} rows, {len(df_for_training.columns)} columns")
        
        with st.expander("📄 View Sample Data"):
            st.dataframe(df_for_training.head())

        import io as _io
        _buf = _io.StringIO()
        df_for_training.to_csv(_buf, index=False)
        _dc1, _dc2 = st.columns([1, 5])
        _dc1.download_button(
            label="⬇ Export CSV",
            data=_buf.getvalue(),
            file_name="training_dataset.csv",
            mime="text/csv",
            help="Download the full loaded dataset"
        )
        _dc2.caption(f"{len(df_for_training):,} rows · {len(df_for_training.columns)} columns")

        st.markdown("### Configuration")
        all_cols = df_for_training.columns.tolist()
        label_col = st.selectbox(
            "Target Label Column (Optional):", 
            ["[Auto-Generate Pseudo Label]"] + all_cols,
            help="Select the column to predict (e.g., isFraud).",
            key="build_label_col"
        )
        
        target_col = None if label_col == "[Auto-Generate Pseudo Label]" else label_col
        
        exclude_cols = st.multiselect(
            "Exclude Columns:",
            [c for c in all_cols if c != target_col],
            help="Features to drop (IDs, names, etc).",
            key="build_exclude_cols"
        )
        
        with st.expander("ℹ️ Help: How to configure columns", expanded=False):
            st.markdown("""
            **1. Target Label Column:**
            This is the "answer" you want the model to predict. 
            - For Fraud Detection, choose `isFraud` (1=Fraud, 0=Normal).
            - If you don't have a label, select `[Auto-Generate Pseudo Label]` and we'll create one using statistical anomalies.

            **2. Exclude Columns:**
            Remove columns that:
            - **Identifying Information:** IDs, Names, Phone Numbers (Privacy & Overfitting risk).
            - **Data Leakage:** Information that wouldn't be available at prediction time (e.g., "fraud_confirmed_date").
            - **High Cardinality:** Text fields with too many unique values.
            """)

        st.markdown("---")
        st.subheader("1.3 Dataset Health Check")
        if st.checkbox("Show Health Check", value=True, key="build_show_health"):
            
            st.markdown("#### Missing Values")
            missing = df_for_training.isnull().sum()
            missing = missing[missing > 0]
            if not missing.empty:
                st.warning(f"⚠️ Missing values detected in {len(missing)} columns.")
                st.dataframe(missing.rename("Missing Count"))
                
                if st.button("🤖 Analyze Missing Data Risks", key="ai_missing_btn"):
                    with st.spinner("AI Analysis..."):
                        llm = init_llm(st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini"))
                        prompt = f"Analyze missing values:\n{missing.to_markdown()}\n\nSuggest imputation strategies."
                        st.session_state.missing_analysis = llm.invoke(prompt).content
                
                if "missing_analysis" in st.session_state:
                    st.info(st.session_state.missing_analysis)
            else:
                st.success("✅ No missing values detected.")
                
            st.markdown("#### Label Distribution")
            if target_col and target_col in df_for_training.columns:
                counts = df_for_training[target_col].value_counts().reset_index()
                counts.columns = [target_col, "Count"]
                st.altair_chart(alt.Chart(counts).mark_bar().encode(
                    x=alt.X(target_col, type='nominal'), y='Count', color=target_col
                ).properties(title=f"Distribution of {target_col}"), use_container_width=True)
                
                if st.button("🤖 Analyze Class Balance", key="ai_balance_btn"):
                    with st.spinner("AI Analysis..."):
                        llm = init_llm(st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini"))
                        prompt = f"Target '{target_col}' distribution:\n{counts.to_markdown()}\n\nIs this imbalanced? Suggest techniques (SMOTE, weighting)."
                        st.session_state.balance_analysis = llm.invoke(prompt).content
                
                if "balance_analysis" in st.session_state:
                    st.info(st.session_state.balance_analysis)

        st.markdown("---")
        st.subheader("1.4 Baseline Model Check")
        if can_control:
            train_baseline_btn = st.button("⚡ Train Baseline Model", key="build_train_baseline")
        else:
            st.button("⚡ Train Baseline Model", key="build_train_baseline", disabled=True, help="Admin access required")
            train_baseline_btn = False

        if train_baseline_btn:
            if not target_col:
                st.error("Please select a Target Label Column first.")
            else:
                with st.spinner("Training Baseline..."):
                    try:
                        temp_df = df_for_training.dropna(subset=[target_col]).copy()
                        if exclude_cols: temp_df = temp_df.drop(columns=exclude_cols, errors='ignore')
                        
                        X = temp_df.drop(columns=[target_col])
                        y = temp_df[target_col]
                        X_num = X.select_dtypes(include=[np.number]).fillna(0)
                        
                        if X_num.empty:
                            st.error("No numeric features found.")
                        else:
                            X_tr, X_te, y_tr, y_te = train_test_split(X_num, y, test_size=0.3, random_state=42)
                            model_base = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
                            model_base.fit(X_tr, y_tr)
                            y_pred = model_base.predict(X_te)
                            
                            acc = accuracy_score(y_te, y_pred)
                            f1 = f1_score(y_te, y_pred, average='weighted')
                            cm = confusion_matrix(y_te, y_pred)
                            
                            st.session_state.baseline_res = {
                                "accuracy": acc,
                                "f1": f1,
                                "cm": cm,
                                "importances": pd.DataFrame({
                                    "Feature": X_num.columns,
                                    "Importance": model_base.feature_importances_
                                }).sort_values("Importance", ascending=False).head(10)
                            }
                    except Exception as e:
                        st.error(f"Baseline failed: {e}")

        if "baseline_res" in st.session_state:
            res = st.session_state.baseline_res
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Preview Accuracy", f"{res['accuracy']:.1%}")
            m2.metric("Preview F1-Score", f"{res['f1']:.2f}")
            
            with m3:
                st.caption("Confusion Matrix (Val)")
                cm_data = []
                for i, actual in enumerate(["Normal", "Fraud"]):
                    for j, pred in enumerate(["Normal", "Fraud"]):
                        cm_data.append({"Actual": actual, "Predicted": pred, "Count": res['cm'][i][j]})
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

            st.markdown("#### Top Drivers (Feature Importance)")
            st.altair_chart(alt.Chart(res['importances']).mark_bar().encode(
                x="Importance", y=alt.Y("Feature", sort="-x")
            ), use_container_width=True)
            
            if st.button("🤖 Analyze Feature Importance", key="ai_feat_imp_btn"):
                 with st.spinner("AI Analysis..."):
                    llm = init_llm(st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini"))
                    prompt = f"Top Features:\n{res['importances'].to_markdown()}\n\nWhy are these predictive? Check for leakage."
                    st.session_state.feat_imp_analysis = llm.invoke(prompt).content
            
            if "feat_imp_analysis" in st.session_state:
                st.info(st.session_state.feat_imp_analysis)

        st.markdown("---")
        st.subheader("1.5 Generate Final Dataset")
        if can_control:
            process_btn = st.button("🚀 Process & Split Data", key="build_process_split")
        else:
            st.button("🚀 Process & Split Data", key="build_process_split", disabled=True, help="Admin access required")
            process_btn = False

        if process_btn:
            with st.spinner("Processing..."):
                try:
                    final_df = df_for_training.copy()
                    if exclude_cols: final_df = final_df.drop(columns=exclude_cols, errors='ignore')
                    
                    result = build_training_dataset(
                        df=final_df, output_dir="data/ml", label_column=target_col
                    )
                    st.session_state.build_result = result
                    st.success("✅ Training Dataset Ready!")
                except Exception as e:
                    st.error(f"Build Failed: {e}")

        if "build_result" in st.session_state:
            res = st.session_state.build_result
            st.json(res)
            
            with st.expander("ℹ️ Learning: How we split the dataset", expanded=False):
                st.markdown("""
                **We use a standard 70/15/15 Data Split Strategy:**
                
                1. **Train (70%)**: The model learns patterns from this data.
                2. **Validation (15%)**: Used to tune the model and prevent overfitting during training.
                3. **Test (15%)**: Held out completely until the end to evaluate true performance.
                """)
                
                st.code("""
# Python Code (sklearn):
# 1. First split: 70% Train, 30% Temp (Val + Test)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42)

# 2. Second split: Split the 30% temp into two equal halves (15% each)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42)
                """, language="python")

