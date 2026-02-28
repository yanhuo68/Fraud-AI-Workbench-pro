import json
import logging
from pathlib import Path
import pandas as pd
import io

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: Path) -> tuple[str, str]:
    """
    Extract text content from a file based on its extension.
    Supports: CSV, PDF, TXT, MD, JSON, Image (OCR), Audio/Video (Transcription).
    Returns: (text_content, doc_type)
    """
    file_path = Path(file_path)
    file_ext = file_path.suffix.lower().lstrip('.')
    content = ""

    try:
        if file_ext == "csv":
            df = pd.read_csv(file_path)
            content = df.to_csv(index=False)
        elif file_ext == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                content += page.extract_text() or ""
        elif file_ext in ("txt", "md"):
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        elif file_ext == "json":
            json_obj = json.loads(file_path.read_text(encoding="utf-8"))
            content = json.dumps(json_obj, indent=2)
        elif file_ext in ("png", "jpg", "jpeg", "webp"):
            from agents.multimodal_agent import describe_image
            content = describe_image(str(file_path))
        elif file_ext in ("mp3", "wav", "m4a", "mp4", "mov", "avi"):
            from agents.multimodal_agent import transcribe_audio
            content = transcribe_audio(str(file_path))
        else:
            logger.warning(f"Unsupported extension for graph extraction: {file_ext}")
            return "", file_ext
            
        return content, file_ext
        
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise
