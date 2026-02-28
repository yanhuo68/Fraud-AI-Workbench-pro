import streamlit as st
from typing import Dict, Any, List

def render_rag_context_inspector(rag_result: Dict[str, Any]):
    """
    Render a visual inspector for RAG retrieval results in Streamlit.
    
    Args:
        rag_result: Dictionary returned by answer_kb_question(return_context=True)
                    Expected keys: 'answer', 'contexts' (list of dicts)
                    Context dict keys: 'content', 'metadata', 'score'
    """
    contexts = rag_result.get("contexts", [])
    
    if not contexts:
        st.info("No context was retrieved for this answer.")
        return

    with st.expander(f"🕵️ RAG Context Inspector ({len(contexts)} chunks retrieved)", expanded=False):
        for i, ctx in enumerate(contexts):
            score = ctx.get("score", 0.0)
            metadata = ctx.get("metadata", {})
            content = ctx.get("content", "")
            source = metadata.get("source", "Unknown Source")
            
            # Create a header with relevance score
            # Note: FAISS scores: lower is better (L2 distance), but sometimes normalized.
            # We'll just display raw score.
            st.markdown(f"**Chunk {i+1}** (Score: `{score:.4f}`)")
            st.caption(f"Source: `{source}`")
            
            # Display content snippet
            st.text_area(
                label="Content",
                value=content,
                height=150,
                key=f"rag_ctx_{i}",
                disabled=True
            )
            st.divider()
