from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from typing import Optional, Any
import logging
import tempfile
import pandas as pd
from api.dependencies import get_current_user

from api.models import ReportGenerateRequest
from agents.pdf_exporter import generate_pdf
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate")
async def generate_analytical_report(payload: ReportGenerateRequest, current_user: Any = Depends(get_current_user)):
    """
    Generate a PDF analytical report.
    Expects data context if generating from ad-hoc analysis.
    """
    try:
        logger.info(f"Generating {payload.format} report of type {payload.analysis_type}")
        
        # 1. Prepare temp file path
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{payload.format}")
        report_path = tmp.name
        tmp.close()
        
        # 2. Extract context
        ctx = payload.data_context or {}
        
        # 3. Generate based on format
        if payload.format.lower() == "pdf":
            # Map context to generate_pdf arguments
            # If context is missing, we use placeholders
            df = None
            if "df" in ctx and isinstance(ctx["df"], list):
                df = pd.DataFrame(ctx["df"])
                
            final_path = generate_pdf(
                sql=ctx.get("sql", "N/A"),
                df=df,
                trend_chart=None, # Cannot easily pass Altair obj via API JSON yet
                reconciliation_text=ctx.get("reconciliation", "N/A"),
                synthesis_text=ctx.get("synthesis", "N/A"),
                output_path=report_path
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {payload.format}")
            
        return FileResponse(
            path=final_path,
            filename=f"fraud_analysis_report.{payload.format}",
            media_type="application/pdf" if payload.format == "pdf" else "application/octet-stream"
        )

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
