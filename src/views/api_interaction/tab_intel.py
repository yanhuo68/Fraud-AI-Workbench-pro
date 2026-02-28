import streamlit as st
import json
from views.api_interaction.helpers import make_request, _ep

def render_intel_tab(api_base_url, available_llms):
    i_tabs = st.tabs(["🤖 Multi-Agent Pipeline", "🔍 Legacy SQL NLQ"])

    # ── Multi-Agent ────────────────────────────────────────────────────────────
    with i_tabs[0]:
        _ep("POST", "/agents/query", "auth")
        st.caption("Full multi-agent RAG pipeline: retrieval → SQL → explanation → reconciliation → synthesis.")

        agent_samples = {
            "Custom question": "",
            "Sample 5 transactions": "Show me a sample of 5 transactions from the database.",
            "Schema check": "What are the names of all tables in the data store?",
            "Suspicious merchants": "Which merchants have suspiciously high transaction volumes?",
            "Flagged entities": "Are there any transactions linked to known high-risk entities?",
            "Fraud ring detection": "Show me customers who share accounts with flagged fraud cases.",
        }

        sel = st.selectbox("Quick Sample", list(agent_samples.keys()))
        default_q = agent_samples[sel] or "Which merchants have suspicious high-volume transactions?"

        with st.expander("📌 Request Schema"):
            st.code(json.dumps({
                "question":      "string — natural language question",
                "llm_id":        "string — e.g. openai:gpt-4o-mini",
                "k_candidates":  "int (1-5) — retrieval candidates",
                "bypass_agents": "bool — skip deep synthesis (faster, avoids timeouts)",
                "rebuild_kb":    "bool — force KB rebuild before query"
            }, indent=2), language="json")

        with st.form("agent_query_form"):
            q  = st.text_area("Question", value=default_q)
            c1, c2 = st.columns(2)
            with c1:
                llm  = st.selectbox("LLM", available_llms, key="agent_llm")
                k    = st.slider("Candidates (k)", 1, 5, 3)
            with c2:
                bypass  = st.checkbox("⚡ Speed Mode (bypass agents)", value=True)
                rebuild = st.checkbox("🔄 Rebuild KB", value=False)
            if st.form_submit_button("🚀 Run Agent Pipeline", use_container_width=True):
                make_request("POST", "/agents/query", api_base_url, payload={
                    "question": q, "llm_id": llm,
                    "k_candidates": k, "bypass_agents": bypass, "rebuild_kb": rebuild
                })

    # ── Legacy SQL NLQ ─────────────────────────────────────────────────────────
    with i_tabs[1]:
        _ep("POST", "/rag/nlq", "auth")
        st.caption("Lightweight SQL NLQ — single-step query without full agent pipeline.")

        nlq_samples = {
            "Custom": "",
            "Top 5 rows": "List the top 5 rows from the main transaction table.",
            "High-value txns": "Show transactions above $5,000.",
            "Customer lookup": "Find all transactions for customer ID 101.",
        }
        sel_nlq = st.selectbox("Quick Sample", list(nlq_samples.keys()), key="nlq_sel")
        default_nlq = nlq_samples[sel_nlq] or "List top 5 transactions"

        with st.expander("📌 Request Schema"):
            st.code(json.dumps({
                "question": "string — natural language SQL question",
                "llm_id":   "string — e.g. openai:gpt-4o-mini"
            }, indent=2), language="json")

        with st.form("nlq_form"):
            nq   = st.text_input("Question", value=default_nlq)
            nllm = st.selectbox("LLM", available_llms, key="nlq_llm")
            if st.form_submit_button("🔍 Run NLQ", use_container_width=True):
                make_request("POST", "/rag/nlq", api_base_url, payload={"question": nq, "llm_id": nllm})
