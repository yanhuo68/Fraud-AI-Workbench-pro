import streamlit as st
import json
from views.api_interaction.helpers import make_request, _ep

def render_models_tab(api_base_url, available_llms):
    m_tabs = st.tabs(["📋 Model Registry", "🎯 ML Scoring", "📝 Report Generation"])

    with m_tabs[0]:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            _ep("GET", "/models/list", "auth")
            st.caption("List all registered ML model versions.")
            if st.button("List ML Models", use_container_width=True, key="list_models"):
                make_request("GET", "/models/list", api_base_url)

        with col_m2:
            _ep("GET", "/models/available", "auth")
            st.caption("Discover available LLMs (Ollama + cloud).")
            if st.button("Discover LLMs", use_container_width=True, key="disc_llms"):
                make_request("GET", "/models/available", api_base_url)

    with m_tabs[1]:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            _ep("POST", "/models/score", "auth")
            st.caption("Score a transaction through a registered LLM/ML model.")
            with st.expander("📌 Request Schema"):
                st.code(json.dumps({
                    "model_id": "string — model identifier",
                    "input_data": {
                        "amount": "number",
                        "merchant": "string",
                        "account_age": "int (days)",
                        "velocity": "int (txns/24h)"
                    }
                }, indent=2), language="json")
            with st.form("models_score_form"):
                m_id  = st.selectbox("Model ID", available_llms, key="models_score_id")
                m_dat = st.text_area("Input Data (JSON)", value='{"amount": 1500, "merchant": "TechStore", "account_age": 180, "velocity": 3}')
                if st.form_submit_button("Run Score", use_container_width=True):
                    try:
                        make_request("POST", "/models/score", api_base_url, payload={"model_id": m_id, "input_data": json.loads(m_dat)})
                    except Exception:
                        st.error("Invalid JSON in input data.")

        with col_s2:
            _ep("POST", "/ml/score", "auth")
            st.caption("Score via trained ML workflow model (XGBoost/RandomForest from ML Workflow tab).")
            with st.expander("📌 Request Schema"):
                st.code(json.dumps({
                    "model_id": "string — versioned ML model ID (from /models/list)",
                    "input_data": {"feature_1": "value", "feature_2": "value"}
                }, indent=2), language="json")
            with st.form("ml_score_form"):
                ml_m_id  = st.text_input("ML Model ID", placeholder="e.g. expert:xgboost_v1")
                ml_m_dat = st.text_area("Input Data (JSON)", value='{"amount": 9999, "num_transactions": 50}', key="ml_score_dat")
                if st.form_submit_button("▶️ ML Score", use_container_width=True):
                    try:
                        make_request("POST", "/ml/score", api_base_url, payload={"model_id": ml_m_id, "input_data": json.loads(ml_m_dat)})
                    except Exception:
                        st.error("Invalid JSON in input data.")

    with m_tabs[2]:
        _ep("POST", "/reports/generate", "auth")
        st.caption("Generate a PDF fraud investigation report.")
        with st.expander("📌 Request Schema"):
            st.code(json.dumps({
                "analysis_type": "full | summary | fraud",
                "format": "pdf",
                "data_context": {
                    "synthesis": "string — executive summary",
                    "sql": "string — SQL query used",
                    "graph_data": "object (optional)",
                    "anomalies": "array (optional)"
                }
            }, indent=2), language="json")
        with st.form("report_form"):
            rtype = st.selectbox("Analysis Type", ["full", "summary", "fraud"])
            rctx  = st.text_area("Data Context (JSON)", value='{"synthesis": "Fraud ring detected involving 3 merchants.", "sql": "SELECT * FROM transactions LIMIT 10"}', height=120)
            if st.form_submit_button("📄 Generate Report", use_container_width=True):
                try:
                    make_request("POST", "/reports/generate", api_base_url, payload={
                        "analysis_type": rtype, "format": "pdf", "data_context": json.loads(rctx)
                    })
                except Exception:
                    st.error("Invalid JSON in data context.")
