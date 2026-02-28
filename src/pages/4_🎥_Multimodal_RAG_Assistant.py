# ==============================================================================
# Refactored Multimodal RAG Assistant Module Entrypoint
# The heavy lifting has been moved to src/views/multimodal_rag/
# ==============================================================================
from views.multimodal_rag.render import render_multimodal_rag

# Execute the isolated render process
render_multimodal_rag()
