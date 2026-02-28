# agents/execution_player.py

"""
Streamlit component for step-by-step replay of LangGraph agent execution.

Features:
- Next / Previous step
- Jump to beginning / end
- Play mode (auto-forward)
- Highlight active node in Mermaid graph
"""

import streamlit as st
import time
from agents.graph_visualizer import build_mermaid_diagram


def render_execution_player(graph, trace):
    if not trace:
        st.info("No trace available for this run.")
        return

    # State management
    if "trace_idx" not in st.session_state:
        st.session_state.trace_idx = 0

    idx = st.session_state.trace_idx
    max_idx = len(trace) - 1
    current_step = trace[idx]

    # ---------------------------------------------------------
    # Controls Row
    # ---------------------------------------------------------
    left, mid, right = st.columns([2, 2, 2])

    with left:
        if st.button("⏮ First"):
            st.session_state.trace_idx = 0

        if st.button("◀ Previous") and idx > 0:
            st.session_state.trace_idx -= 1

    with mid:
        if st.button("▶ Next") and idx < max_idx:
            st.session_state.trace_idx += 1

        if st.button("⏭ Last"):
            st.session_state.trace_idx = max_idx

    with right:
        if st.button("🎬 Auto Play"):
            for i in range(idx, max_idx + 1):
                st.session_state.trace_idx = i
                time.sleep(0.7)
                st.rerun()

    st.markdown("---")

    # ---------------------------------------------------------
    # Active Node Diagram
    # ---------------------------------------------------------
    active_node = current_step["node"]
    st.markdown(f"### 🟡 Active Node: **{active_node}**")

    mermaid_code = build_mermaid_diagram(
        list(graph.nodes.keys()),
        [(a, b) for a in graph.edges for b in graph.edges[a]],
        active_node=active_node
    )

    st.markdown(
        f"""
        ```mermaid
        {mermaid_code}
        """
        )
        
    # ---------------------------------------------------------
    # Step Details
    # ---------------------------------------------------------
    st.markdown("### 🔍 Step Input")
    st.json(current_step["input"])

    st.markdown("### 🟩 Step Output")
    st.json(current_step["output"])

    if "exception" in current_step:
        st.error(f"⚠️ Exception occurred in node {current_step['node']}")
        from agents.error_inspector import render_error_inspector
        render_error_inspector(current_step["exception"])
        return

    st.markdown("---")
    st.caption(f"Step {idx+1} of {max_idx+1}")
