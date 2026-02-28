import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_available_llms(include_local: bool = True) -> List[str]:
    """
    Thin wrapper around Registry-aware llm_router.get_available_llms.
    """
    try:
        from agents.llm_router import get_available_llms as get_llms
        return get_llms(include_local=include_local)
    except ImportError:
        # Fallback if circular import or missing router
        llms = ["openai:gpt-4o-mini", "openai:gpt-4o", "deepseek:deepseek-chat"]
        if include_local:
             from agents.local_llm_discovery import list_ollama_models, detect_lmstudio
             llms.extend(list_ollama_models())
             llms.extend(detect_lmstudio())
        return llms
