# agents/rag_inspector.py

"""
RAG Context Inspector for Streamlit.

Visualizes:
- Retrieved chunks
- Source metadata
- Similarity scores
- Full text in expanders
"""

from typing import Dict, Any, List
import streamlit as st
import pandas as pd


def render_rag_context_inspector(result: Dict[str, Any]):
    """
    Expects dict with:
    {
      "answer": str,
      "contexts": [
        {"content": str, "metadata": dict, "score": float},
        ...
      ]
    }
    """
    contexts: List[Dict[str, Any]] = result.get("contexts", [])

    st.markdown("### 🔎 RAG Context Inspector")

    if not contexts:
        st.info("No retrieved context documents to display.")
        return

    # Build summary table
    rows = []
    for idx, ctx in enumerate(contexts, start=1):
        src = ctx.get("metadata", {}).get("source", "unknown")
        score = ctx.get("score", None)
        snippet = ctx.get("content", "")[:180].replace("\n", " ")
        rows.append(
            {
                "Rank": idx,
                "Source": src,
                "Score": score,
                "Snippet": snippet + ("..." if len(ctx.get("content", "")) > 180 else ""),
            }
        )

    df = pd.DataFrame(rows)

    st.subheader("📊 Retrieved Chunks Overview")
    st.dataframe(df)

    # Optional: score bar chart (if scores are numeric)
    if all(isinstance(r["Score"], (int, float)) for r in rows):
        st.subheader("📈 Similarity Scores (lower may be better depending on index)")
        chart_df = df.set_index("Source")[["Score"]]
        st.bar_chart(chart_df)

    st.subheader("📄 Full Context Chunks")
    for idx, ctx in enumerate(contexts, start=1):
        src = ctx.get("metadata", {}).get("source", "unknown")
        score = ctx.get("score", None)
        with st.expander(f"Chunk #{idx} — Source: {src} — Score: {score}"):
            st.write(ctx.get("content", ""))
            st.json(ctx.get("metadata", {}))
