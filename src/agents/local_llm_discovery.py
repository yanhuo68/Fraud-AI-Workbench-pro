# agents/local_llm_discovery.py
import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

def list_ollama_models():
    """Return a list of locally installed Ollama models via REST API."""
    urls = ["http://localhost:11434/api/tags", "http://host.docker.internal:11434/api/tags"]
    for url in urls:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                logger.info(f"Ollama Success: Found {len(models)} models at {url}")
                return [f"local_ollama:{m}" for m in models]
            else:
                logger.warning(f"Ollama Warning: {url} returned {resp.status_code}")
        except requests.exceptions.ConnectionError:
            logger.debug(f"Ollama: Connection refused at {url}")
        except Exception as e:
                # logger.warning(f"Ollama Warning: {url} returned {resp.status_code}")
                pass # The new LM Studio function removes this type of logging, so keeping consistent.
        except requests.exceptions.ConnectionError:
            # logger.debug(f"Ollama: Connection refused at {url}")
            pass # The new LM Studio function removes this type of logging, so keeping consistent.
        except Exception as e:
            # logger.debug(f"Ollama Error at {url}: {e}")
            continue
    logger.info("Ollama: No models found on any host.")
    return []

def detect_lmstudio():
    """Check if LM Studio server is running."""
    urls = ["http://localhost:1234/v1/models", "http://host.docker.internal:1234/v1/models"]
    for url in urls:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                return [f"local_lmstudio:{m}" for m in models]
                logger.warning(f"LM Studio Warning: {url} returned {resp.status_code}")
        except requests.exceptions.ConnectionError:
            logger.debug(f"LM Studio: Connection refused at {url}")
        except Exception as e:
            logger.debug(f"LM Studio Error at {url}: {e}")
            continue

    logger.info("LM Studio: No models found on any host.")
    return []
