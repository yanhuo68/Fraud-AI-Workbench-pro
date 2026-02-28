import time
import requests
import sys
from pathlib import Path

from config.settings import settings
from agents.local_llm_discovery import list_ollama_models, detect_lmstudio
from agents.llm_router import get_available_llms

print("Starting discovery benchmark...")

start = time.time()
ollama = list_ollama_models()
print(f"Ollama discovery took: {time.time() - start:.2f}s (Found: {len(ollama)})")

start = time.time()
lmstudio = detect_lmstudio()
print(f"LM Studio discovery took: {time.time() - start:.2f}s (Found: {len(lmstudio)})")

start = time.time()
all_llms = get_available_llms()
print(f"Total discovery took: {time.time() - start:.2f}s (Total: {len(all_llms)})")

print("\nDiscovered LLMs:")
for llm in all_llms:
    print(f" - {llm}")
