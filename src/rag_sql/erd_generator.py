# rag_sql/erd_generator.py

"""
ERD diagram generator using mermaid syntax.

Generates:
- Entity blocks for each table
- PK annotation
- FK arrows
- Column + type lists

Output:
- Mermaid ERD diagram to render in Streamlit
- (Optional) save as PNG using graphviz
"""

from typing import Dict, List
import pandas as pd
from graphviz import Digraph

def build_mermaid_erd(
    tables: Dict[str, pd.DataFrame],
    pkfk_map: Dict[str, Dict],
) -> str:
    """
    Generates Mermaid ERD diagram text.
    tables: {table_name: df}
    pkfk_map: {table_name: {"primary_key": col, "foreign_keys": [(table_A, colA, table_B, pkB)]}}
    """
    lines = []
    lines.append("erDiagram")

    # --- Build table definitions ---
    for table, df in tables.items():
        lines.append(f"    {table} {{")
        pk = pkfk_map.get(table, {}).get("primary_key")

        for col in df.columns:
            pd_type = str(df[col].dtype)
            # mark PK with "*"
            if pk and pk == col:
                lines.append(f"        * {col} {pd_type}")
            else:
                lines.append(f"          {col} {pd_type}")
        lines.append("    }")

    # --- Add FK Relationships ---
    for table, meta in pkfk_map.items():
        for fk in meta.get("foreign_keys", []):
            # fk: (table_A, colA, table_B, pkB)
            table_A, colA, table_B, pkB = fk
            # Mermaid relationship notation:
            # TableA }o--|| TableB : "colA → pkB"
            lines.append(f'    {table_A} }}o--|| {table_B} : "{colA} → {pkB}"')

    return "\n".join(lines)

def build_png_erd(tables, pkfk_map, output_path="data/erd/erd.png"):
    dot = Digraph("ERD", format="png")
    dot.attr(rankdir="LR")

    # Add nodes
    for table, df in tables.items():
        pk = pkfk_map.get(table, {}).get("primary_key")
        label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>"
        label += f"<TR><TD COLSPAN='2'><B>{table}</B></TD></TR>"

        for col in df.columns:
            if pk and pk == col:
                label += f"<TR><TD><B>{col}</B></TD><TD>PK</TD></TR>"
            else:
                label += f"<TR><TD>{col}</TD><TD></TD></TR>"

        label += "</TABLE>>"
        dot.node(table, label=label, shape="plaintext")

    # Add FK edges
    for table, meta in pkfk_map.items():
        for fk in meta.get("foreign_keys", []):
            table_A, colA, table_B, pkB = fk
            dot.edge(table_A, table_B, label=f"{colA} → {pkB}")

    dot.render(output_path, cleanup=True)
    return output_path