# agents/graph_visualizer.py

"""
Dynamic visualization utilities for LangGraph agent workflows.
Produces Mermaid diagram strings for Streamlit display.
"""

from typing import Dict, List
import json


def extract_graph_structure(graph) -> Dict:
    """
    Extracts nodes and edges from a LangGraph graph object.
    Works with LCEL-style graph.nodes and graph.edges.
    """
    nodes = list(graph.nodes.keys())

    edges = []
    for from_node, to_nodes in graph.edges.items():
        for to_node in to_nodes:
            edges.append((from_node, to_node))

    return {"nodes": nodes, "edges": edges}


def build_mermaid_diagram(nodes: List[str], edges: List[tuple]) -> str:
    """
    Build a Mermaid diagram for LangGraph DAG.
    """
    mermaid = "flowchart TD\n"

    # Add nodes
    for n in nodes:
        safe = n.replace(" ", "_")
        mermaid += f'    {safe}["{n}"];\n'

    # Add edges
    for a, b in edges:
        a_safe = a.replace(" ", "_")
        b_safe = b.replace(" ", "_")
        mermaid += f"    {a_safe} --> {b_safe};\n"

    return mermaid


def get_graph_mermaid(graph) -> str:
    """
    High-level wrapper that extracts structure + builds mermaid code.
    """
    structure = extract_graph_structure(graph)
    return build_mermaid_diagram(structure["nodes"], structure["edges"])
