from fastapi import APIRouter, HTTPException, Depends
from typing import Any
from api.dependencies import get_current_user
from pydantic import BaseModel
import logging

from rag_sql.sql_utils import run_sql_query, SQLValidationError
from agents.sql_ranking_agent import generate_sql_candidates, pick_best_sql
from utils.schema_utils import build_schema_text_from_tables
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class NLQRequest(BaseModel):
    """Natural language query request."""
    question: str
    llm_id: str = "openai:gpt-4o-mini"


@router.post("/nlq")
def natural_language_query(payload: NLQRequest, current_user: Any = Depends(get_current_user)):
    """
    Convert natural language question to SQL and execute it.
    
    Args:
        payload: NLQ request with question and optional LLM ID
    
    Returns:
        JSON with SQL query and preview results
    """
    try:
        logger.info(f"Processing NLQ: {payload.question}")
        
        from utils.schema_utils import build_schema_text_from_tables
        schema_text = build_schema_text_from_tables()
        
        # Generate SQL candidates
        try:
            candidates = generate_sql_candidates(
                question=payload.question,
                llm_id=payload.llm_id,
                schema_text=schema_text,
                k=3
            )
            logger.info(f"Generated {len(candidates)} SQL candidates")
        except Exception as e:
            logger.error(f"Failed to generate SQL candidates: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate SQL: {str(e)}"
            )
        
        if not candidates:
            raise HTTPException(
                status_code=400,
                detail="No SQL candidates generated"
            )
        
        # Pick best SQL
        try:
            ranked = pick_best_sql(candidates)
            best_sql = ranked["best"]["sql"]
            logger.info(f"Selected best SQL: {best_sql}")
        except Exception as e:
            logger.error(f"Failed to rank SQL candidates: {e}")
            # Fall back to first candidate
            best_sql = candidates[0]
        
        # Execute SQL with validation
        try:
            df, cols = run_sql_query(
                best_sql,
                db_path=settings.db_path,
                validate=True,
                timeout_seconds=settings.sql_timeout_seconds,
                max_rows=settings.sql_max_rows
            )
            logger.info(f"SQL executed successfully: {len(df)} rows returned")
        except SQLValidationError as e:
            logger.warning(f"SQL validation failed: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"SQL validation failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"SQL execution failed: {str(e)}"
            )
        
        return {
            "sql": best_sql,
            "preview": df.head(50).to_dict(orient="records"),
            "total_rows": len(df),
            "columns": cols
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"NLQ processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )
