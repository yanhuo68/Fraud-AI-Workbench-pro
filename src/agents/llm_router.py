# agents/llm_router.py
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.ollama import ChatOllama
import requests
import os
from config.settings import settings

def get_available_llms(include_local: bool = True):
    from agents.local_llm_discovery import list_ollama_models, detect_lmstudio
    from utils.version_manager import ModelManager
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    start_total = time.time()

    base_models = [
        "openai:gpt-4o-mini",
        "openai:gpt-4o",
        "deepseek:deepseek-chat",
        "google:gemini-1.5-pro",
        "anthropic:claude-3-5-sonnet-20240620",
        "anthropic:claude-3-opus-20240229",
    ]

    ollama = []
    lmstudio = []
    
    if include_local:
        logger.info("Discovering local LLMs...")
        s = time.time()
        ollama = list_ollama_models()
        logger.info(f"Ollama discovery took {time.time()-s:.2f}s")
        
        s = time.time()
        lmstudio = detect_lmstudio()
        logger.info(f"LM Studio discovery took {time.time()-s:.2f}s")
    
    # 3. Discover Registered Models (Fine-Tuned & Experts)
    registered_models = []
    try:
        s = time.time()
        model_mgr = ModelManager()
        models = model_mgr.get_all_models()
        for m in models:
            if m.get('training_params', {}).get('type') == 'ollama_expert':
                registered_models.append(f"expert:{m['id']}")
            else:
                registered_models.append(f"fine-tuned:{m['id']}")
        logger.info(f"Registry lookup took {time.time()-s:.2f}s")
    except Exception as e:
        logger.error(f"Registry lookup failed: {e}")
        pass

    logger.info(f"Total LLM discovery took {time.time()-start_total:.2f}s")
    return base_models + registered_models + ollama + lmstudio + ["custom:http"]

class ExpertPromptWrapper:
    """Wraps an Ollama model with a saved expert prompt template."""
    def __init__(self, llm, template):
        self.llm = llm
        self.template = template
    
    def invoke(self, input_data):
        # Handle different input types (string vs messages)
        if isinstance(input_data, str):
            content = input_data
        elif hasattr(input_data, 'content'):
            content = input_data.content
        else:
            content = str(input_data)
            
        full_prompt = self.template.replace("{{TRANSACTION_DATA}}", content).replace("{TRANSACTION_DATA}", content)
        return self.llm.invoke(full_prompt)

class MLXAdapterWrapper:
    """Wraps MLX model with adapters for inference."""
    def __init__(self, model_id, adapter_path, base_model):
        self.model_id = model_id
        self.adapter_path = adapter_path
        self.base_model = base_model

    def invoke(self, input_data):
        import subprocess
        content = str(input_data.content if hasattr(input_data, 'content') else input_data)
        
        # Simplified generation for RAG/Chat use
        try:
            result = subprocess.run(
                ['mlx_lm.generate', '--model', self.base_model, 
                 '--adapter-path', str(self.adapter_path), '--prompt', content, '--max-tokens', '300'],
                capture_output=True, text=True, timeout=60
            )
            class Response:
                def __init__(self, c): self.content = c
            return Response(result.stdout.strip())
        except Exception as e:
            class Error:
                def __init__(self, c): self.content = c
            return Error(f"MLX Error: {str(e)}")

def _get_local_url(port: int, path: str = ""):
    """Try to find the correct local endpoint (Docker vs Local)."""
    for host in ["localhost", "host.docker.internal"]:
        url = f"http://{host}:{port}{path}"
        try:
            # Quick check if reachable
            requests.get(url.replace("/v1", ""), timeout=0.5)
            return url
        except Exception:
            continue
    return f"http://localhost:{port}{path}"

def get_api_key(key_name: str) -> str:
    """
    Priority:
    1. Streamlit session state (sidebar input)
    2. config.settings value
    """
    import streamlit as st
    sidebar_mapping = {
        "OPENAI_API_KEY": "sidebar_openai_key",
        "DEEPSEEK_API_KEY": "sidebar_deepseek_key",
        "GOOGLE_API_KEY": "sidebar_google_key",
        "ANTHROPIC_API_KEY": "sidebar_anthropic_key"
    }
    
    state_key = sidebar_mapping.get(key_name)
    if state_key and state_key in st.session_state and st.session_state[state_key]:
        return st.session_state[state_key]
    
    from config.settings import settings
    if key_name == "OPENAI_API_KEY": return settings.openai_api_key
    if key_name == "DEEPSEEK_API_KEY": return settings.deepseek_api_key
    if key_name == "GOOGLE_API_KEY": return settings.google_api_key
    if key_name == "ANTHROPIC_API_KEY": return settings.anthropic_api_key
    
    return os.getenv(key_name, "")

def init_llm(model_id: str):
    # --- Registered Experts (Ollama + Prompt) ---
    if model_id.startswith("expert:"):
        from utils.version_manager import ModelManager
        expert_id = model_id.split(":", 1)[1]
        model_info = ModelManager().get_model(expert_id)
        if not model_info:
            raise ValueError(f"Expert model not found: {expert_id}")
            
        training_params = model_info.get('training_params', {})
        base_llm_id = training_params.get('base_model', 'ollama:llama3:8b')
        template = training_params.get('prompt_template', '')
        
        base_llm = init_llm(base_llm_id)
        return ExpertPromptWrapper(base_llm, template)

    # --- Registered Fine-Tuned (MLX) ---
    elif model_id.startswith("fine-tuned:"):
        from utils.version_manager import ModelManager
        model_id_internal = model_id.split(":", 1)[1]
        model_mgr = ModelManager()
        model_info = model_mgr.get_model(model_id_internal)
        if not model_info:
            raise ValueError(f"Fine-tuned model not found: {model_id_internal}")
            
        adapter_path = model_mgr.get_model_path(model_id_internal)
        base_model = model_info.get('training_params', {}).get('base_model', 'mlx-community/Llama-3.2-1B-Instruct-4bit')
        
        return MLXAdapterWrapper(model_id_internal, adapter_path, base_model)

    # --- OpenAI ---
    if model_id.startswith("openai:"):
        name = model_id.split(":", 1)[1]
        return ChatOpenAI(
            model=name,
            api_key=get_api_key("OPENAI_API_KEY"),
            temperature=0.1,
        )

    # --- DeepSeek ---
    elif model_id.startswith("deepseek:"):
        name = model_id.split(":", 1)[1]
        return ChatOpenAI(
            model=name,
            api_key=get_api_key("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            temperature=0.1,
        )

    # --- Ollama ---
    elif model_id.startswith("local_ollama:") or model_id.startswith("ollama:"):
        name = model_id.split(":", 1)[1]
        base_url = _get_local_url(11434)
        return ChatOllama(
            model=name,
            base_url=base_url,
            temperature=0.1,
        )

    # --- LM Studio ---
    elif model_id.startswith("local_lmstudio:"):
        name = model_id.split(":", 1)[1]
        base_url = _get_local_url(1234, "/v1")
        return ChatOpenAI(
            model=name,
            base_url=base_url,
            api_key="lm-studio",
            temperature=0.1,
        )

    # --- Google Gemini ---
    elif model_id.startswith("google:"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        name = model_id.split(":", 1)[1]
        return ChatGoogleGenerativeAI(
            model=name,
            google_api_key=get_api_key("GOOGLE_API_KEY"),
            temperature=0.1,
        )

    # --- Anthropic Claude ---
    elif model_id.startswith("anthropic:"):
        from langchain_anthropic import ChatAnthropic
        name = model_id.split(":", 1)[1]
        return ChatAnthropic(
            model=name,
            anthropic_api_key=get_api_key("ANTHROPIC_API_KEY"),
            temperature=0.1,
        )

    # --- Custom HTTP ---
    elif model_id.startswith("custom:http"):
        url = os.getenv("CUSTOM_LLM_URL", "http://localhost:8080/v1")
        model = os.getenv("CUSTOM_LLM_MODEL", "local-model")
        return ChatOpenAI(model=model, base_url=url, api_key="none")

    raise ValueError(f"Unknown LLM: {model_id}")
