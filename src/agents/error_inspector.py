# agents/error_inspector.py

"""
Unified error inspector for LangGraph workflows.
Provides:
- Exception capture
- Traceback extraction
- Node-level error tagging
- LLM-powered root-cause analysis
- Suggested fixes
- Streamlit UI renderer
"""

import traceback
import streamlit as st
from agents.llm_router import init_llm


def capture_exception(node_name: str, exception: Exception):
    """
    Converts an exception into a portable structure that can be stored in trace.
    """
    tb_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

    return {
        "node": node_name,
        "error_type": type(exception).__name__,
        "message": str(exception),
        "traceback": tb_str,
    }


def annotate_trace_with_error(trace, error_obj):
    """
    Append error info into the trace sequence.
    """
    trace.append({
        "node": error_obj["node"],
        "input": {},
        "output": {"error": "Exception occurred"},
        "exception": error_obj,
    })
    return trace


# ---------------------------------------------------------
# LLM-Based Error Analysis
# ---------------------------------------------------------
def analyze_error_with_llm(error_obj, llm_model="openai:gpt-4o-mini"):
    """
    Use LLM to interpret the exception and give suggestions.
    """
    llm = init_llm(llm_model)

    prompt = f"""
    You are an AI debugging specialist. Analyze the following exception and produce:

    1. Root cause (in plain English)
    2. Where likely in the pipeline the error originated (LangGraph node: {error_obj['node']})
    3. Potential fixes (precise code-level suggestions)
    4. If the error suggests corruption or inconsistent schema, propose validation steps

    Error Type: {error_obj['error_type']}
    Message: {error_obj['message']}
    Traceback:
    {error_obj['traceback']}

    Provide a structured answer with headings.
    """

    response = llm.invoke(prompt)
    return response.content


# ---------------------------------------------------------
# Streamlit UI Renderer
# ---------------------------------------------------------
def render_error_inspector(error_obj):
    st.error(f"❌ Error in node **{error_obj['node']}**: {error_obj['error_type']}")

    st.markdown("### 🔍 Error Message")
    st.code(error_obj["message"])

    st.markdown("### 📄 Traceback")
    st.code(error_obj["traceback"])

    st.markdown("### 🧠 LLM Root-Cause Analysis")
    with st.spinner("Analyzing error using LLM…"):
        analysis = analyze_error_with_llm(error_obj)
    st.markdown(analysis)
