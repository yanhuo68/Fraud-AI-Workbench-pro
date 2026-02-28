# rag_sql/langgraph_flow.py
from __future__ import annotations
import os
import sqlite3
import time
from typing import TypedDict, Any, List, Dict
import logging

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

from config.logging_conf import setup_logging, get_logger
from config.settings import settings
from agents.llm_router import init_llm
from agents.critic_agent import explain_sql_result

# Initialize logging
setup_logging(log_file=settings.log_file, level=settings.log_level)
logger = get_logger(__name__)

DB_PATH = settings.db_path  # Use centralized DB path



class FraudState(TypedDict):
    question: str
    sql_query: str | None
    result: List[tuple] | None
    error: str | None
    critique: str | None
    trace: List[Dict[str, Any]]  # node execution trace


def get_llm(model_id: str | None = None):
    """
    model_id can be passed from Streamlit; if None, falls back to env or default.
    """
    if model_id is None:
        model_id = os.getenv("DEFAULT_LLM_ID", "openai:gpt-4o-mini")
    return init_llm(model_id)


def _record_trace(state: FraudState, node_name: str, start: float, end: float):
    trace = state.get("trace") or []
    trace.append(
        {
            "node": node_name,
            "start": start,
            "end": end,
            "duration_sec": end - start,
        }
    )
    state["trace"] = trace
    return state


def sql_planner(state: FraudState) -> FraudState:
    """LLM node: NL question -> SQL."""
    start = time.time()

    # model_id may be injected via state
    model_id = state.get("llm_id") or None
    llm = get_llm(model_id)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert SQL assistant for a fraud detection dataset. "
                    "Table name: transactions. "
                    "Columns include: step, type, amount, oldbalanceOrg, newbalanceOrig, "
                    "oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud, etc. "
                    "Return ONLY a valid SQLite SELECT query. Do not include backticks or comments."
                ),
            ),
            ("human", "Question: {question}"),
        ]
    )

    sql = llm.invoke(
        prompt.format_messages(question=state["question"])
    ).content.strip()

    state["sql_query"] = sql

    end = time.time()
    state = _record_trace(state, "sql_planner", start, end)
    return state


def sql_executor(state: FraudState) -> FraudState:
    """Run the SQL on SQLite with validation."""
    start = time.time()
    sql = state.get("sql_query")

    if not sql:
        state["error"] = "No SQL to execute."
        end = time.time()
        state = _record_trace(state, "sql_executor", start, end)
        return state

    try:
        from rag_sql.sql_utils import run_sql_query
        from config.settings import settings
        
        # Execute with validation
        df, cols = run_sql_query(
            sql,
            db_path=settings.db_path,
            validate=True,
            timeout_seconds=settings.sql_timeout_seconds,
            max_rows=settings.sql_max_rows
        )
        
        # Convert DataFrame to list of tuples for compatibility
        rows = [tuple(row) for row in df.values]
        state["result"] = rows
        
    except Exception as e:
        error_msg = f"SQL error: {e}"
        logger.error(error_msg)
        state["error"] = error_msg

    end = time.time()
    state = _record_trace(state, "sql_executor", start, end)
    return state



def critic_node(state: FraudState) -> FraudState:
    """LLM-based explanation / critique of SQL + results."""
    start = time.time()

    if state.get("error"):
        end = time.time()
        state = _record_trace(state, "critic", start, end)
        return state

    sql = state.get("sql_query")
    rows = state.get("result") or []

    if not sql:
        state["critique"] = "No SQL to critique."
        end = time.time()
        state = _record_trace(state, "critic", start, end)
        return state

    question = state.get("question", "")
    state["critique"] = explain_sql_result(question, sql, rows)

    end = time.time()
    state = _record_trace(state, "critic", start, end)
    return state


def build_graph():
    g = StateGraph(FraudState)

    g.add_node("sql_planner", sql_planner)
    g.add_node("sql_executor", sql_executor)
    g.add_node("critic", critic_node)

    g.set_entry_point("sql_planner")
    g.add_edge("sql_planner", "sql_executor")
    g.add_edge("sql_executor", "critic")
    g.add_edge("critic", END)

    return g.compile()


graph = build_graph()


def ask_sql(question: str, llm_id: str | None = None) -> FraudState:
    """
    Entry point for Streamlit / tests.
    Includes trace + critique.
    """
    state: FraudState = {
        "question": question,
        "sql_query": None,
        "result": None,
        "error": None,
        "critique": None,
        "trace": [],
        "llm_id": llm_id,  # custom extra key
    }
    return graph.invoke(state)
