import streamlit as st
from pathlib import Path
import pandas as pd
import io

from utils.dashboard_state import (
    init_state,
    build_schema_text_from_tables,
)

from rag_sql.sql_utils import run_sql_query
from rag_sql.knowledge_base import answer_kb_question

from agents.llm_router import init_llm
from agents.rag_inspector import render_rag_context_inspector
from components.sidebar import render_global_sidebar, enforce_page_access

# Initialize State
init_state()
enforce_page_access("2_🧠_SQL_RAG_Assistant")
render_global_sidebar()

from agents.sql_ranking_agent import generate_sql_candidates, pick_best_sql
from agents.sql_recovery_agent import repair_sql
from agents.sql_fallback_agent import generate_fallback_sql
from agents.join_explanation_agent import explain_join_query
from agents.sql_reconciliation_agent import reconcile_sql_results
from agents.hybrid_synthesis_agent import hybrid_synthesis

from agents.eda_agent import compute_basic_eda, eda_narrative
from agents.anomaly_agent import detect_anomalies_iqr, anomaly_narrative
from agents.fraud_risk_agent import add_fraud_risk_score, fraud_risk_narrative
from agents.trend_chart_agent import build_trend_chart, generate_trend_insights
from agents.pdf_exporter import generate_pdf
from agents.sql_improvement_agent import suggest_sql_improvements
from agents.llm_router import get_available_llms

st.title("🧠 SQL RAG Assistant (Multi-Agent)")

# ─────────────────────────────────────────────────────────────────────────────
# DB TABLE DISCOVERY  (respects SYSTEM_TABLES filter)
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3
import logging
from config.settings import settings
from utils.data_manager import SYSTEM_TABLES

available_tables = []
try:
    if settings.db_path_obj.exists():
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            available_tables = [
                r[0] for r in cursor.fetchall() if r[0] not in SYSTEM_TABLES
            ]
except Exception as e:
    st.error(f"Failed to fetch tables from database: {e}")

if not available_tables:
    st.warning("No tables found in the database. Please clean/upload data in the **Data Hub** page.")
    st.stop()

# Auto-start session state if empty but tables exist
if not st.session_state.uploaded_tables:
    for t in available_tables:
        st.session_state.uploaded_tables[t] = f"docs/schema_{t}.md"

# ─────────────────────────────────────────────────────────────────────────────
# STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
if "sql_rag_results" not in st.session_state:
    st.session_state.sql_rag_results = {
        "question": "",
        "candidates": [],
        "sql_text": "",
        "df": None,
        "explanation": "",
        "reconciliation": "",
        "hybrid_report": "",
        "trend_chart": None,
        "trend_insights": "",
        "eda_summary": None,
        "eda_insights": "",
        "anomalies": None,
        "anomaly_insights": "",
        "risk_narrative": "",
        "improvements": "",
        "rag_result": None
    }

# NEW: Investigation chat history
if "sql_investigation_history" not in st.session_state:
    st.session_state.sql_investigation_history = []   # list of {question, sql, summary, row_count}

# ─────────────────────────────────────────────────────────────────────────────
# ERD HELPER — builds a Mermaid ER diagram from SQLite PRAGMA
# ─────────────────────────────────────────────────────────────────────────────
def build_erd_mermaid(tables: list[str]) -> str:
    """Generate a Mermaid erDiagram string from SQLite schema."""
    lines = ["erDiagram"]
    fk_lines = []
    try:
        with sqlite3.connect(settings.db_path) as con:
            for tbl in tables:
                cols = con.execute(f"PRAGMA table_info('{tbl}')").fetchall()
                if not cols:
                    continue
                col_defs = []
                for col in cols:
                    # col: (cid, name, type, notnull, dflt_value, pk)
                    cname = col[1].replace(" ", "_")
                    ctype = (col[2] or "TEXT").split("(")[0].upper() or "TEXT"
                    pk_marker = " PK" if col[5] else ""
                    col_defs.append(f'        {ctype} {cname}{pk_marker}')
                lines.append(f'    {tbl} {{')
                lines.extend(col_defs)
                lines.append('    }')

                # Foreign keys
                fks = con.execute(f"PRAGMA foreign_key_list('{tbl}')").fetchall()
                for fk in fks:
                    # fk: (id, seq, table, from, to, ...)
                    ref_table = fk[2]
                    from_col  = fk[3]
                    to_col    = fk[4]
                    if ref_table in tables:
                        fk_lines.append(
                            f'    {tbl} }}o--|| {ref_table} : "{from_col}→{to_col}"'
                        )
    except Exception as e:
        lines.append(f"    %% ERD error: {e}")
    lines.extend(fk_lines)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_right:
    sql_llm_id = st.session_state.get("global_llm_id", "gpt-4o-mini")

    selected_table = st.selectbox(
        "Default table for fallback (if JOIN fails)",
        list(st.session_state.uploaded_tables.keys()),
    )

    # Schema-based Question Generator
    if st.button("🎲 Suggest Questions"):
        with st.spinner("Analyzing schema to generate questions..."):
            try:
                schema = build_schema_text_from_tables()
                llm = init_llm(sql_llm_id)
                prompt = (
                    "You are a SQL data analyst assistant. Analyze the database schema below and "
                    f"suggest 3 interesting, analytical questions that a business user might ask about the '{selected_table}' table.\n"
                    "CRITICAL KEY RULES:\n"
                    "1. Base questions ONLY on the exact tables and columns provided below. DO NOT invent tables.\n"
                    f"2. Your questions MUST involve the '{selected_table}' table. If '{selected_table}' explicitly has NO relationships listed in the schema, ask standalone questions ONLY about '{selected_table}'; DO NOT assume it joins to other tables.\n"
                    f"3. If '{selected_table}' DOES have Explicit Relationships (Foreign Keys) listed, you MAY suggest questions that join it to those specific related tables.\n"
                    "4. Focus on aggregations and trends where possible.\n\n"
                    f"Schema:\n{schema}\n\n"
                    "Output ONLY the 3 questions, one per line, without numbering or extra text."
                )
                resp = llm.invoke(prompt)
                questions = [line.strip("- 123. ") for line in resp.content.strip().split("\n") if line.strip()]
                st.session_state.suggested_questions = questions[:3]
            except Exception as e:
                st.error(f"Failed to generate questions: {e}")

    st.markdown("---")

    # ── NEW: Table ERD Diagram ─────────────────────────────────────────────
    with st.expander("🗺️ Table Relationship Diagram (ERD)", expanded=False):
        st.caption("Auto-generated from your loaded tables using PRAGMA foreign_key_list.")
        erd_tables = available_tables
        if erd_tables:
            erd_mermaid = build_erd_mermaid(erd_tables)
            st.markdown(f"```mermaid\n{erd_mermaid}\n```")
        else:
            st.info("No tables loaded yet.")

    # ── Investigation History ──────────────────────────────────────────────
    if st.session_state.sql_investigation_history:
        st.markdown("---")
        st.markdown("#### 🕐 Investigation History")
        for idx, entry in enumerate(reversed(st.session_state.sql_investigation_history)):
            with st.expander(f"Q{len(st.session_state.sql_investigation_history)-idx}: {entry['question'][:55]}…", expanded=False):
                st.code(entry["sql"], language="sql")
                st.caption(f"Returned {entry['row_count']} rows")
                if entry.get("summary"):
                    st.markdown(entry["summary"])
                # Quick re-run button
                if st.button("↩ Re-run this question", key=f"rerun_{idx}"):
                    st.session_state.selected_suggestion = entry["question"]
                    st.rerun()

        if st.button("🗑 Clear History", key="clear_sql_hist"):
            st.session_state.sql_investigation_history = []
            st.rerun()

with col_left:
    # Pre-fill from suggestions if available
    default_question = ""

    if "suggested_questions" in st.session_state and st.session_state.suggested_questions:
        st.caption("Suggested Questions:")
        cols = st.columns(len(st.session_state.suggested_questions))
        for i, q in enumerate(st.session_state.suggested_questions):
            if cols[i].button(f"Q{i+1}", help=q, key=f"btn_q{i}"):
                st.session_state.selected_suggestion = q

    if "selected_suggestion" in st.session_state:
        default_question = st.session_state.selected_suggestion

    sql_question = st.text_area(
        "Ask a question about your data (natural language):",
        value=default_question,
        placeholder="e.g., What is the average transaction amount by type over the last 30 days?",
        height=120,
    )

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
if st.button("🚀 Run SQL + RAG Pipeline", type="primary"):
    if not sql_question.strip():
        st.warning("Please enter a question.")
        st.stop()

    schema_text = build_schema_text_from_tables()
    st.session_state.sql_rag_results["question"] = sql_question

    # 1) Generate SQL candidates
    with st.spinner("Generating SQL candidates..."):
        candidates = generate_sql_candidates(
            question=sql_question,
            llm_id=sql_llm_id,
            schema_text=schema_text,
            k=3,
        )
        st.session_state.sql_rag_results["candidates"] = candidates

    # 2) Rank candidates
    with st.spinner("Ranking candidates..."):
        ranked = pick_best_sql(candidates)

    best = ranked["best"]
    sql_text = best["sql"]
    best_df = best["df"]
    best_error = best["error"]

    # 2A) Recovery agent
    if best_error:
        repaired_sql = repair_sql(
            question=sql_question, bad_sql=sql_text,
            error_message=best_error, schema_text=schema_text,
            llm_id=sql_llm_id,
        )
        try:
            repaired_df, _ = run_sql_query(repaired_sql)
            sql_text = repaired_sql
            best_df = repaired_df
        except:
            pass

    # 2B) Fallback mode
    if best_df is None or (isinstance(best_df, pd.DataFrame) and best_df.empty):
        fallback_sql = generate_fallback_sql(
            question=sql_question, table=selected_table,
            schema_text=schema_text, llm_id=sql_llm_id,
        )
        try:
            fallback_df, _ = run_sql_query(fallback_sql)
            best_df = fallback_df
            sql_text = fallback_sql
        except:
            pass

    # Store SQL Result
    st.session_state.sql_rag_results["sql_text"] = sql_text
    st.session_state.sql_rag_results["df"] = best_df

    # Agents Pipeline
    with st.spinner("Generating Advanced Analytics..."):
        st.session_state.sql_rag_results["explanation"] = explain_join_query(
            question=sql_question, sql=sql_text, df=best_df, schema_text=schema_text, llm_id=sql_llm_id
        )
        st.session_state.sql_rag_results["reconciliation"] = reconcile_sql_results(
            question=sql_question, candidate_records=ranked["all_candidates"], schema_text=schema_text, llm_id=sql_llm_id
        )

        # Hybrid
        rag_res = answer_kb_question(sql_question, llm_id=sql_llm_id, return_context=True, k=3)
        st.session_state.sql_rag_results["rag_result"] = rag_res
        st.session_state.sql_rag_results["hybrid_report"] = hybrid_synthesis(
            question=sql_question, sql=sql_text, df=best_df,
            rag_contexts=rag_res.get("contexts", []) if isinstance(rag_res, dict) else [],
            schema_text=schema_text, llm_id=sql_llm_id
        )

        # Insights
        chart, t_col = build_trend_chart(best_df)
        st.session_state.sql_rag_results["trend_chart"] = chart
        if chart is not None:
            st.session_state.sql_rag_results["trend_insights"] = generate_trend_insights(
                df=best_df, question=sql_question, llm_id=sql_llm_id, schema_text=schema_text
            )

        # EDA & Anomalies
        if best_df is not None and not best_df.empty:
            eda_sum = compute_basic_eda(best_df)
            st.session_state.sql_rag_results["eda_summary"] = eda_sum
            st.session_state.sql_rag_results["eda_insights"] = eda_narrative(
                df=best_df, question=sql_question, eda_summary=eda_sum, schema_text=schema_text, llm_id=sql_llm_id
            )
            anom, thresh = detect_anomalies_iqr(best_df)
            st.session_state.sql_rag_results["anomalies"] = anom
            if anom is not None and not anom.empty:
                st.session_state.sql_rag_results["anomaly_insights"] = anomaly_narrative(
                    question=sql_question, df=best_df, anomalies=anom, thresholds=thresh, schema_text=schema_text, llm_id=sql_llm_id
                )

            # Risk
            scored_df = add_fraud_risk_score(best_df)
            st.session_state.sql_rag_results["df"] = scored_df
            st.session_state.sql_rag_results["risk_narrative"] = fraud_risk_narrative(
                df=scored_df, question=sql_question, schema_text=schema_text, llm_id=sql_llm_id
            )

        st.session_state.sql_rag_results["improvements"] = suggest_sql_improvements(
            question=sql_question, sql=sql_text, schema_text=schema_text, llm_id=sql_llm_id
        )

    # ── Append to investigation history ───────────────────────────────────
    row_count = len(best_df) if isinstance(best_df, pd.DataFrame) else 0
    history_entry = {
        "question": sql_question,
        "sql": sql_text,
        "row_count": row_count,
        "summary": st.session_state.sql_rag_results.get("hybrid_report", "")[:300] + "…"
    }
    # Avoid exact duplicates of the last question
    if (not st.session_state.sql_investigation_history or
            st.session_state.sql_investigation_history[-1]["question"] != sql_question):
        st.session_state.sql_investigation_history.append(history_entry)

# ─────────────────────────────────────────────────────────────────────────────
# RENDERING SECTION
# ─────────────────────────────────────────────────────────────────────────────
res = st.session_state.sql_rag_results
if res["sql_text"]:
    st.markdown("---")
    st.header("📊 Investigative Findings")

    with st.expander("🧪 SQL Candidate Lab", expanded=False):
        for i, cand in enumerate(res["candidates"], 1):
            st.markdown(f"#### Candidate {i}")
            st.code(cand, language="sql")

    st.subheader("🏆 Winning Query")
    st.code(res["sql_text"], language="sql")

    if res["df"] is not None:
        df_display = res["df"]
        st.subheader("📋 Data Preview")
        st.dataframe(df_display.head(100), use_container_width=True)

        # ── NEW: CSV Export ────────────────────────────────────────────────
        csv_buf = io.StringIO()
        df_display.to_csv(csv_buf, index=False)
        exp_col1, exp_col2 = st.columns([1, 4])
        exp_col1.download_button(
            label="⬇ Export CSV",
            data=csv_buf.getvalue(),
            file_name="sentinel_query_results.csv",
            mime="text/csv",
            help="Download all result rows as CSV",
        )
        exp_col2.caption(f"{len(df_display):,} rows · {len(df_display.columns)} columns")

        st.subheader("🧠 SQL Analysis")
        st.markdown(res["explanation"])
        st.info(res["reconciliation"])

    # Reports
    st.markdown("---")
    st.subheader("📘 Hybrid Synthesis Report")
    st.markdown(res["hybrid_report"])

    if res["trend_chart"] is not None:
        st.markdown("---")
        st.subheader("📈 Trend Analysis")
        st.altair_chart(res["trend_chart"], use_container_width=True)
        st.markdown(res["trend_insights"])

    if res["eda_summary"]:
        with st.expander("🔍 Exploratory Data Analysis & Anomalies"):
            if res["eda_summary"]["numeric_summary"] is not None:
                st.dataframe(res["eda_summary"]["numeric_summary"])
            st.markdown(res["eda_insights"])
            if res["anomalies"] is not None:
                st.warning(f"Detected {len(res['anomalies'])} anomalies")
                st.dataframe(res["anomalies"].head(20))
                st.markdown(res["anomaly_insights"])

    if res["risk_narrative"]:
        st.markdown("---")
        st.subheader("🚨 Fraud Risk Intelligence")
        st.markdown(res["risk_narrative"])

    with st.expander("🛠 SQL Improvement Suggestions"):
        st.markdown(res["improvements"])

    # Export Section
    st.markdown("---")
    st.subheader("📄 Report Export")
    if st.button("Generate PDF Hub"):
        with st.spinner("Forging PDF Report..."):
            pdf_path = generate_pdf(
                sql=res["sql_text"],
                df=res["df"],
                trend_chart=res["trend_chart"],
                reconciliation_text=res["reconciliation"],
                synthesis_text=res["hybrid_report"],
                output_path="analysis_report.pdf",
            )
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇ Download Analysis (PDF)",
                    data=f,
                    file_name="sentinel_investigation.pdf",
                    mime="application/pdf",
                )

    # Context Inspector
    if res["rag_result"]:
        st.markdown("---")
        with st.expander("🔍 RAG Context Inspector"):
            render_rag_context_inspector(res["rag_result"])

else:
    st.info("Start a new investigation by running the SQL pipeline above.")
