# agents/agents_ui.py

"""
Agents UI module for Streamlit dashboard.
Provides agent console, workflow runners, logs, JSON breadcrumbs,
and full LangGraph interaction APIs.
"""

import streamlit as st
import json
from agents.llm_router import init_llm


# ---------------------------------------------------------
# Utility: Pretty JSON renderer
# ---------------------------------------------------------
def pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


# ---------------------------------------------------------
# Agent UI Main Entry
# ---------------------------------------------------------
def render_agents_ui():
    st.header("🤖 Multi-Agent Console")

    # Check graph availability
    if "langgraph_workflow" not in st.session_state:
        st.warning("⚠️ No agent graphs have been loaded.")
        return

    graphs = st.session_state["langgraph_workflow"]

    # Select a workflow
    graph_name = st.selectbox("Select Workflow", list(graphs.keys()))
    graph = graphs[graph_name]

    st.write(f"### Workflow selected: **{graph_name}**")

    # ----------------------------------------------
    # User Input
    # ----------------------------------------------
    st.subheader("🧠 Ask Agents a Question")

    user_query = st.text_area("Enter your query", placeholder="e.g., 'Find fraud transactions for account XYZ'")

    selected_llm = st.selectbox(
        "LLM Model",
        [
            "openai:gpt-4o-mini",
            "openai:gpt-4o",
            "deepseek:deepseek-chat",
            "ollama:llama3",
            "ollama:deepseek-r1",
        ]
    )

    run_button = st.button("🚀 Run Agents")

    # Execution state
    if "agent_runs" not in st.session_state:
        st.session_state.agent_runs = []

    # ----------------------------------------------
    # Run Workflow
    # ----------------------------------------------
    if run_button and user_query.strip():
        st.info("Running workflow...")
        llm = init_llm(selected_llm)

        with st.spinner("Executing agents…"):
            # Execute graph
            result, trace = execute_graph_with_trace(graph, user_query, llm)
            
            if "error" in result:
                st.error("Agent workflow failed with an exception.")
                st.session_state.agent_runs.append({
                    "query": user_query,
                    "result": result,
                    "trace": trace,
                    "exception": result["exception"]
                })

            else:
                st.session_state.agent_runs.append({
                    "query": user_query,
                    "result": result,
                    "trace": trace,
                    "exception": None
                })


        # Save run to history
        run_record = {"query": user_query, "result": result, "trace": trace}
        st.session_state.agent_runs.append(run_record)

        st.success("Agent workflow completed.")

    # ----------------------------------------------
    # Show run history
    # ----------------------------------------------
    st.subheader("📜 Agent Run History")

    if not st.session_state.agent_runs:
        st.info("No runs yet.")
        return

    for idx, run in enumerate(st.session_state.agent_runs[::-1]):
        st.markdown(f"### Run #{len(st.session_state.agent_runs)-idx}")
        st.write(f"**Query:** {run['query']}")

        with st.expander("🟦 Final Result"):
            st.json(run["result"])

        with st.expander("🔍 Execution Trace (Raw JSON)"):
            st.code(pretty_json(run["trace"]))
    if run["exception"]:
        st.warning("⚠️ Error occurred in this run.")

        with st.expander("🔴 Error Inspector"):
            from agents.error_inspector import render_error_inspector
            render_error_inspector(run["exception"])



# ---------------------------------------------------------
# Graph Execution + Trace Capture
# ---------------------------------------------------------
def execute_graph_with_trace(graph, query, llm):
    """
    Executes the LangGraph workflow step-by-step and captures full trace logs.
    """

    trace = []
    state = {"input": query, "llm": llm}

    # A simplified execution loop (works with typical LangGraph DAGs)
    # If using LCEL pipelines, adjust for actual input/output names.
    pending = [node for node in graph.nodes if graph.is_entry_point(node)]

    visited = set()

    while pending:
        node = pending.pop(0)
        visited.add(node)

        node_fn = graph.nodes[node].get("callable", None)
        if node_fn is None:
            output = {"error": "Node has no callable"}
        else:
            output = node_fn(state)

        # Capture execution trace
        trace.append({
            "node": node,
            "input": state.copy(),
            "output": output
        })

        # Update state with node output
        if isinstance(output, dict):
            state.update(output)
        else:
            state["last_output"] = output

        # Add next nodes
        if node in graph.edges:
            for nxt in graph.edges[node]:
                if nxt not in visited:
                    pending.append(nxt)

    return state, trace

from agents.error_inspector import capture_exception, annotate_trace_with_error


def execute_graph_with_trace(graph, query, llm):
    """
    Executes LangGraph as before, but now with:
    - Exception wrapping
    - Node-level error tagging
    - Error trace embedding
    """

    trace = []
    state = {"input": query, "llm": llm}

    pending = [node for node in graph.nodes if graph.is_entry_point(node)]
    visited = set()

    while pending:
        node = pending.pop(0)
        visited.add(node)

        node_fn = graph.nodes[node].get("callable", None)
        if node_fn is None:
            output = {"error": "Node has no callable"}
        else:
            try:
                output = node_fn(state)

            except Exception as e:
                # Convert to structured error object
                error_obj = capture_exception(node, e)

                # Attach error to trace
                annotate_trace_with_error(trace, error_obj)

                # Stop execution
                return {"error": True, "last_node": node, "exception": error_obj}, trace

        trace.append({
            "node": node,
            "input": state.copy(),
            "output": output
        })

        if isinstance(output, dict):
            state.update(output)
        else:
            state["last_output"] = output

        if node in graph.edges:
            for nxt in graph.edges[node]:
                if nxt not in visited:
                    pending.append(nxt)

    return state, trace
