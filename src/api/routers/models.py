from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from api.dependencies import get_current_user

from api.models import ModelScoreRequest, ModelScoreResponse
from utils.version_manager import ModelManager
from agents.llm_router import init_llm

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/list")
async def list_models(current_user: Any = Depends(get_current_user)):
    """List all registered models (Fine-tuned, Experts, etc.)"""
    try:
        model_mgr = ModelManager()
        models = model_mgr.get_all_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available")
async def list_available_llms(current_user: Any = Depends(get_current_user)):
    """List all discovered LLM IDs (Local + Cloud + Fine-tuned)"""
    try:
        from agents.llm_router import get_available_llms
        llms = get_available_llms()
        return {"llms": llms}
    except Exception as e:
        logger.error(f"Failed to discover LLMs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score", response_model=ModelScoreResponse)
async def score_with_model(payload: ModelScoreRequest, current_user: Any = Depends(get_current_user)):
    """
    Unified scoring endpoint.
    Automatically handles:
    - expert:ID (Ollama with Prompt)
    - fine-tuned:ID (MLX Adapter)
    - vanilla models (ollama:..., openai:...)
    """
    try:
        logger.info(f"Scoring request using model: {payload.model_id}")
        
        # 1. Initialize the LLM/Wrapper
        # init_llm handles the prefixed IDs (expert:, fine-tuned:) 
        # as well as standard IDs.
        llm = init_llm(payload.model_id)
        
        # 2. Prepare Input
        # For experts/LLMs, we usually pass a string. 
        # If input_data is a dict, we convert to string or use a specific key.
        if isinstance(payload.input_data, dict):
            import json
            input_str = json.dumps(payload.input_data)
        else:
            input_str = str(payload.input_data)
            
        # 3. Invoke
        response = llm.invoke(input_str)
        
        # 4. Format Response
        # Some wrappers return objects with .content, others might return strings
        content = response.content if hasattr(response, 'content') else str(response)
        
        return ModelScoreResponse(
            prediction=content,
            metadata={
                "model_id": payload.model_id,
                "input_type": type(payload.input_data).__name__
            }
        )

    except Exception as e:
        logger.error(f"Scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
