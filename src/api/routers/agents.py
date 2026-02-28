from fastapi import APIRouter, HTTPException, Depends
from api.dependencies import get_current_user
import logging
import pandas as pd
from typing import List, Dict, Any

from api.models import AgentQueryRequest, AgentQueryResponse
from agents.sql_ranking_agent import generate_sql_candidates, pick_best_sql
from agents.sql_recovery_agent import repair_sql
from agents.join_explanation_agent import explain_join_query
from agents.sql_reconciliation_agent import reconcile_sql_results
from agents.hybrid_synthesis_agent import hybrid_synthesis
from rag_sql.knowledge_base import answer_kb_question
from rag_sql.sql_utils import run_sql_query
from agents.anomaly_agent import detect_anomalies_iqr
from agents.fraud_risk_agent import add_fraud_risk_score, fraud_risk_narrative
from utils.schema_utils import build_schema_text_from_tables
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=AgentQueryResponse)
def agentic_query(payload: AgentQueryRequest, current_user: Any = Depends(get_current_user)):
    """
    Full Multi-Agent RAG Pipeline:
    1. Generate SQL candidates
    2. Rank & Select best
    3. Self-repair if needed
    4. Reconcile results
    5. Hybrid Synthesis (SQL + Vector KB)
    6. Insights (Anomalies, Fraud Risk)
    """
    try:
        logger.info(f"Starting agentic query: {payload.question}")
        schema_text = build_schema_text_from_tables()

        # 1. SQL Generation
        candidates = generate_sql_candidates(
            question=payload.question,
            llm_id=payload.llm_id,
            schema_text=schema_text,
            k=payload.k_candidates
        )
        if not candidates:
            raise HTTPException(status_code=400, detail="Could not generate SQL for this question.")

        # 2. Ranking
        ranked = pick_best_sql(candidates)
        best = ranked["best"]
        sql_text = best["sql"]
        best_df = best["df"]
        best_err = best["error"]

        # 3. Recovery
        if best_err or best_df is None:
            logger.info("SQL failed, attempting recovery...")
            sql_text = repair_sql(
                question=payload.question,
                bad_sql=sql_text,
                error_message=str(best_err or "Empty result"),
                schema_text=schema_text,
                llm_id=payload.llm_id
            )
            try:
                best_df, _ = run_sql_query(sql_text)
            except Exception as e:
                logger.error(f"Recovery failed: {e}")
                raise HTTPException(status_code=500, detail=f"SQL failed even after repair: {e}")

        # 4. Explanation & Reconciliation (Skip if bypass enabled)
        explanation = "Skipped (Bypass Mode)"
        recon_text = "Skipped (Bypass Mode)"
        
        if not payload.bypass_agents:
            explanation = explain_join_query(
                question=payload.question,
                sql=sql_text,
                df=best_df.head(20) if best_df is not None else None,
                schema_text=schema_text,
                llm_id=payload.llm_id
            )
            recon_text = reconcile_sql_results(
                question=payload.question,
                candidate_records=ranked["all_candidates"], 
                schema_text=schema_text,
                llm_id=payload.llm_id
            )
        else:
            logger.info("Bypassing explanation and reconciliation for speed.")

        # 5. Hybrid RAG Synthesis (Skip if bypass enabled)
        synthesis = "Skipped (Bypass Mode)"
        if not payload.bypass_agents:
            rag_result = answer_kb_question(
                payload.question,
                llm_id=payload.llm_id,
                return_context=True,
                k=3
            )
            contexts = rag_result.get("contexts", []) if isinstance(rag_result, dict) else []
            
            synthesis = hybrid_synthesis(
                question=payload.question,
                sql=sql_text,
                df=best_df.head(20) if best_df is not None else None,
                rag_contexts=contexts,
                schema_text=schema_text,
                llm_id=payload.llm_id
            )
        else:
            logger.info("Bypassing hybrid synthesis for speed.")

        # 6. Insights
        anomalies_list = None
        if best_df is not None and not best_df.empty:
            anomalies, _ = detect_anomalies_iqr(best_df)
            if anomalies is not None:
                anomalies_list = anomalies.to_dict(orient="records")
        
        fraud_report = "Skipped (Bypass Mode)"
        if not payload.bypass_agents and best_df is not None and not best_df.empty:
            scored_df = add_fraud_risk_score(best_df)
            fraud_report = fraud_risk_narrative(
                df=scored_df.head(20),
                question=payload.question,
                schema_text=schema_text,
                llm_id=payload.llm_id
            )

        return AgentQueryResponse(
            sql=sql_text,
            explanation=explanation,
            reconciliation=recon_text,
            synthesis=synthesis,
            results_preview=best_df.head(50).to_dict(orient="records") if best_df is not None else [],
            total_rows=len(best_df) if best_df is not None else 0,
            columns=best_df.columns.tolist() if best_df is not None else [],
            anomalies=anomalies_list,
            fraud_risk_report=fraud_report
        )

    except Exception as e:
        logger.error(f"Agentic query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
