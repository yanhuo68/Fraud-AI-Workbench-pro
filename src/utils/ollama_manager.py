import requests
import os
import json
from datetime import datetime

# Default to host.docker.internal if not set, assuming app runs in docker and ollama on host
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

def get_ollama_models():
    """Fetch list of installed models from Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("models", [])
            # Format nicely
            formatted = []
            for m in models:
                # Calculate size in GB
                size_gb = m.get("size", 0) / (1024**3)
                formatted.append({
                    "name": m["name"],
                    "size": f"{size_gb:.2f} GB",
                    "modified": m.get("modified_at", "")[:10],  # YYYY-MM-DD
                    "details": m.get("details", {})
                })
            return formatted
        else:
            return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []

def pull_ollama_model(model_name):
    """Trigger a model pull. Returns a generator for streaming progress."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/pull"
        # Streaming POST request
        response = requests.post(url, json={"name": model_name, "stream": True}, stream=True, timeout=60)
        
        if response.status_code != 200:
            return None
            
        return response.iter_lines()
    except Exception as e:
        print(f"Error pulling model: {e}")
        return None

def delete_ollama_model(model_name):
    """Delete a model from Ollama."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/delete"
        resp = requests.delete(url, json={"name": model_name}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Error deleting model: {e}")
        return False

def check_ollama_connection():
    """Simple check if Ollama is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/", timeout=2)
        return resp.status_code == 200
    except:
        return False
