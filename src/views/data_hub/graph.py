import streamlit as st
import requests
from views.data_hub.utils import get_headers, API_URL

def render_graph_section():
    headers = get_headers()
    st.markdown("---")
    st.header("🕸️ Graph Store Visualization")

    if st.button("Refresh Graph View"):
        st.session_state.refresh_graph = True

    # Logic to fetch and display graph
    try:
        with st.spinner("Fetching graph structure..."):
            resp = requests.get(f"{API_URL}/admin/graph-data", headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                nodes = data.get("nodes", [])
                edges = data.get("edges", [])
                
                if not nodes:
                    st.info("Graph is empty. Upload data or run SQL to populate it.")
                else:
                    st.metric("Total Nodes", len(nodes))
                    st.metric("Total Relationships", len(edges))
                    
                    # Build Interactive Graph (streamlit-agraph)
                    from streamlit_agraph import agraph, Node, Edge, Config
                    
                    agraph_nodes = []
                    agraph_edges = []
                    
                    # Define style mapping
                    type_style = {
                       "Person": {"color": "#FF6B6B", "shape": "circularImage", "image": "https://img.icons8.com/color/48/user-male-circle--v1.png"},
                       "Company": {"color": "#4ECDC4", "shape": "circularImage", "image": "https://img.icons8.com/color/48/company.png"},
                       "Organization": {"color": "#4ECDC4", "shape": "circularImage", "image": "https://img.icons8.com/color/48/organization.png"},
                       "Location": {"color": "#45B7D1", "shape": "circularImage", "image": "https://img.icons8.com/color/48/marker.png"},
                       "Transaction": {"color": "#C7F464", "shape": "circularImage", "image": "https://img.icons8.com/color/48/transaction.png"},
                       "Document": {"color": "#F7FFF7", "shape": "circularImage", "image": "https://img.icons8.com/color/48/file.png"},
                       "Table": {"color": "#FFE66D", "shape": "circularImage", "image": "https://img.icons8.com/color/48/database.png"}, 
                       "Email": {"color": "#FF9F1C", "shape": "circularImage", "image": "https://img.icons8.com/color/48/email.png"}
                    }
                    
                    # Add Nodes
                    for n in nodes:
                        label = n.get("label", "Node")
                        group = n.get("group", "Node")
                        node_id = n["id"]
                        
                        style = type_style.get(group, {"color": "#9EE493", "shape": "dot"})
                        
                        display_label = label[:20] + "..." if len(label) > 20 else label
                        
                        agraph_nodes.append(Node(
                            id=node_id,
                            label=display_label,
                            title=f"{group}: {label}\n{n.get('properties', '')}",
                            size=25,
                            shape=style.get("shape", "dot"),
                            image=style.get("image", ""),
                            color=style.get("color")
                        ))
                    
                    # Add Edges
                    for e in edges:
                        agraph_edges.append(Edge(
                            source=e["source"],
                            target=e["target"],
                            label=e["label"],
                            color="#B0B0B0"
                        ))
                    
                    # Configuration
                    config = Config(
                        width="100%",
                        height=950,
                        directed=True,
                        physics=True,
                        hierarchical=False,
                        nodeHighlightBehavior=True,
                        highlightColor="#F7A7A6",
                        collapsible=False,
                        node={'labelProperty': 'label'},
                        link={'labelProperty': 'label', 'renderLabel': True},
                        interaction={"navigationButtons": True, "zoomView": True} 
                    )
                    
                    st.caption(f"Network Visualization: {len(nodes)} Nodes, {len(edges)} Relationships. (Scroll to Zoom, Drag to Move)")
                    return_value = agraph(nodes=agraph_nodes, edges=agraph_edges, config=config)

                    # ── Node Click Detail Panel ──
                    if return_value:
                        clicked_id = return_value
                        clicked_node = next((n for n in nodes if str(n.get("id")) == str(clicked_id)), None)
                        if clicked_node:
                            st.markdown("---")
                            st.subheader(f"🔍 Node Detail: `{clicked_node.get('label', clicked_id)}`")
                            grp = clicked_node.get('group', 'Unknown')
                            st.markdown(f"**Type:** `{grp}`")

                            props = clicked_node.get('properties', {})
                            if props and isinstance(props, dict):
                                detail_cols = st.columns(2)
                                for idx, (k, v) in enumerate(props.items()):
                                    detail_cols[idx % 2].markdown(f"**{k}:** {v}")
                            elif isinstance(props, str) and props:
                                st.markdown(props)

                            outgoing = [e for e in edges if str(e.get('source')) == str(clicked_id)]
                            incoming = [e for e in edges if str(e.get('target')) == str(clicked_id)]
                            nb_col1, nb_col2 = st.columns(2)
                            with nb_col1:
                                st.markdown(f"**➡️ Outgoing Connections ({len(outgoing)})**")
                                for e in outgoing[:10]:
                                    tgt_node = next((n for n in nodes if str(n.get('id')) == str(e.get('target'))), None)
                                    tgt_label = tgt_node.get('label', e.get('target')) if tgt_node else e.get('target')
                                    st.markdown(f"  `{e.get('label')}` → **{tgt_label}**")
                            with nb_col2:
                                st.markdown(f"**⬅️ Incoming Connections ({len(incoming)})**")
                                for e in incoming[:10]:
                                    src_node = next((n for n in nodes if str(n.get('id')) == str(e.get('source'))), None)
                                    src_label = src_node.get('label', e.get('source')) if src_node else e.get('source')
                                    st.markdown(f"  **{src_label}** → `{e.get('label')}`")
                        else:
                            st.info(f"Node `{clicked_id}` selected — no detail found.")

            else:
                st.error(f"⚠️ **Failed to fetch graph data:** {resp.text}")
                with st.expander("🛠️ Troubleshooting Guide"):
                    st.markdown("""
                    1. **Check Infrastructure**: Ensure the Neo4j container is running (`docker ps`).
                    2. **Wait for Health**: Neo4j can take 30-60s to start its Bolt protocol.
                    3. **Logs**: Run `docker logs fraud_neo4j` to check for startup errors.
                    4. **Rebuild**: If errors persist, use the 'Rebuild Graph' button in the admin sidebar.
                    """)
                
    except Exception as e:
        st.error(f"🚨 **Error visualizing graph:** {e}")
        st.info("💡 Tip: This might be a transient connection error. Try clicking 'Refresh Graph View' in a few moments.")

    # =============================================================
    # GRAPH DATABASE EVALUATION PANEL
    # =============================================================
    st.markdown("---")
    st.header("🔬 Graph Database Evaluation")
    st.markdown("*A deep diagnostic of your Graph Store — infrastructure health, query performance, data quality, and retrieval capability.*")

    eval_col_l, eval_col_r = st.columns([2, 1])
    with eval_col_l:
        run_eval = st.button("▶ Run Full Evaluation", type="primary", use_container_width=True)
    with eval_col_r:
        st.caption("Runs ~10 Cypher diagnostics. Usually takes < 5 seconds.")

    if run_eval:
        with st.spinner("Running evaluation... Please wait."):
            try:
                eval_resp = requests.get(f"{API_URL}/admin/graph-evaluation", headers=headers, timeout=60)
                if eval_resp.status_code == 200:
                    ev = eval_resp.json()
                    st.session_state["graph_eval_result"] = ev
                else:
                    st.error(f"Evaluation failed: {eval_resp.text}")
            except Exception as e:
                st.error(f"Could not reach evaluation endpoint: {e}")

    if "graph_eval_result" in st.session_state:
        ev = st.session_state["graph_eval_result"]
        summary = ev.get("summary", {})
        health  = ev.get("health", {})
        perf    = ev.get("performance", {})
        quality = ev.get("quality", {})
        retrieval = ev.get("retrieval", {})

        score = summary.get("score", 0)
        grade = summary.get("grade", "?")
        grade_color = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🔴"}.get(grade, "⚪")
        
        score_pct = score / 100.0
        st.progress(score_pct, text=f"{grade_color} Overall Score: **{score}/100** (Grade **{grade}**)")
        
        with st.expander("📋 Issues & Recommendations", expanded=(score < 90)):
            for issue in summary.get("issues", []):
                if "healthy" in issue.lower() or "no major" in issue.lower():
                    st.success(f"✅ {issue}")
                else:
                    st.warning(f"⚠️ {issue}")
        
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["🏥 Health", "⚡ Performance", "🔍 Quality", "🎯 Retrieval"])
        
        with tab1:
            st.subheader("Infrastructure Health Checks")
            
            bolt = health.get("bolt_connectivity", {})
            if bolt.get("status") == "ok":
                st.success(f"✅ **Bolt Connectivity**: OK  — latency `{bolt.get('latency_ms')} ms`")
            else:
                st.error(f"❌ **Bolt Connectivity**: {bolt.get('detail', 'Failed')}")

            server = health.get("server_info", {})
            if server:
                versions = server.get("versions", ["?"])
                st.info(f"🗄️ **Neo4j Server**: {server.get('name', '?')} v{versions[0] if versions else '?'} ({server.get('edition', '?')} Edition)")
            
            lbl = health.get("label_distribution", {})
            if isinstance(lbl, dict) and "error" not in lbl and lbl:
                st.markdown("**Node Distribution by Label:**")
                cols = st.columns(min(len(lbl), 5))
                for i, (label, count) in enumerate(sorted(lbl.items(), key=lambda x: -x[1] if isinstance(x[1], (int, float)) else 0)):
                    cols[i % len(cols)].metric(label, count)
            
            rel = health.get("relationship_distribution", {})
            if isinstance(rel, dict) and "error" not in rel and rel:
                st.markdown("**Relationship Types:**")
                import pandas as pd
                rel_df = pd.DataFrame(list(rel.items()), columns=["Relationship Type", "Count"])
                rel_df = rel_df.sort_values("Count", ascending=False).reset_index(drop=True)
                st.dataframe(rel_df, use_container_width=True)

        with tab2:
            st.subheader("Query Performance Profiling")

            perf_rows = []
            for name, details in perf.items():
                status = details.get("status", "?")
                latency = details.get("latency_ms")
                result_val = details.get("result", {})
                readable = ", ".join(f"{k}={v}" for k, v in result_val.items() if k != "n") if isinstance(result_val, dict) else str(result_val)
                perf_rows.append({
                    "Query": name.replace("_", " ").title(),
                    "Status": "✅" if status == "ok" else "❌",
                    "Latency (ms)": latency if latency is not None else "N/A",
                    "Result": readable
                })

            if perf_rows:
                import pandas as pd
                perf_df = pd.DataFrame(perf_rows)
                st.dataframe(perf_df, use_container_width=True)
            
            latencies = [r["Latency (ms)"] for r in perf_rows if isinstance(r["Latency (ms)"], (int, float))]
            if latencies:
                avg_lat = sum(latencies) / len(latencies)
                max_lat = max(latencies)
                latency_col1, latency_col2 = st.columns(2)
                latency_col1.metric("Avg Query Latency", f"{avg_lat:.1f} ms")
                latency_col2.metric("Max Query Latency", f"{max_lat:.1f} ms", 
                                    delta="⚠️ Slow" if max_lat > 500 else "✅ Fast",
                                    delta_color="inverse" if max_lat > 500 else "normal")

        with tab3:
            st.subheader("Graph Data Quality Metrics")
            
            q_col1, q_col2, q_col3, q_col4 = st.columns(4)
            
            total_nodes = quality.get("total_nodes", "?")
            total_edges = quality.get("total_edges", "?")
            orphans = quality.get("orphaned_nodes", "?")
            dups = quality.get("duplicate_nodes_estimate", "?")
            missing = quality.get("nodes_missing_label_property", "?")
            density = quality.get("graph_density", "?")
            
            q_col1.metric("Total Nodes", total_nodes)
            q_col2.metric("Total Edges", total_edges)
            q_col3.metric("Orphaned Nodes", orphans, 
                          delta="⚠️ Clean up" if isinstance(orphans, int) and orphans > 10 else "✅ OK",
                          delta_color="inverse" if isinstance(orphans, int) and orphans > 10 else "normal")
            q_col4.metric("Duplicate Nodes (~)", dups,
                          delta="⚠️ Check data" if isinstance(dups, int) and dups > 0 else "✅ Clean",
                          delta_color="inverse" if isinstance(dups, int) and dups > 0 else "normal")
            
            st.markdown("---")
            
            q2_col1, q2_col2 = st.columns(2)
            q2_col1.metric("Graph Density", f"{density:.6f}" if isinstance(density, float) else density,
                           help="edges / (N × (N-1)). Values near 0 = sparse; near 1 = dense.")
            q2_col2.metric("Nodes Missing ID Prop", missing,
                           delta="⚠️ Add identifiers" if isinstance(missing, int) and missing > 5 else "✅ OK",
                           delta_color="inverse" if isinstance(missing, int) and missing > 5 else "normal")

        with tab4:
            st.subheader("Retrieval Quality Assessment")
            
            d2 = retrieval.get("depth2_reachability", {})
            if "error" not in d2:
                r_col1, r_col2, r_col3 = st.columns(3)
                r_col1.metric("Depth-2 Reachable Pairs", d2.get("reachable_pairs", 0))
                r_col2.metric("Avg Path Length", d2.get("avg_path_length", 0))
                r_col3.metric("Traversal Latency", f"{d2.get('latency_ms', '?')} ms")
            else:
                st.error(f"Depth-2 Traversal Error: {d2.get('error')}")
            
            kw = retrieval.get("keyword_search_fraud", {})
            if "error" not in kw:
                st.info(f"🔍 **Keyword Search** ('fraud'): `{kw.get('matches', 0)}` matching nodes found in `{kw.get('latency_ms', '?')} ms`")
            else:
                st.warning(f"⚠️ Keyword search error: {kw.get('error')}")
            
            cov = retrieval.get("node_connectivity_coverage_pct")
            if cov is not None and not isinstance(cov, dict):
                cov_color = "normal" if cov > 60 else "inverse"
                cov_delta = "✅ Well-connected" if cov > 60 else "⚠️ Many isolated nodes"
                st.metric("Node Connectivity Coverage", f"{cov}%", delta=cov_delta, delta_color=cov_color,
                          help="% of nodes having at least one relationship.")
            
            st.markdown("---")
            st.caption("*Retrieval quality reflects how well the graph can support graph-based RAG queries. Higher coverage and lower latency = better RAG performance.*")
