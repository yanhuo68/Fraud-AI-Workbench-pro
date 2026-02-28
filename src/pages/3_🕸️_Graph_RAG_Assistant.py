import streamlit as st
import logging
from config.settings import settings
from agents.llm_utils import get_available_llms
from agents.llm_router import init_llm
from utils.pdf_gen import create_report
from components.sidebar import render_global_sidebar, enforce_page_access
import os

logger = logging.getLogger(__name__)

from utils.dashboard_state import init_state
init_state()
enforce_page_access("3_🕸️_Graph_RAG_Assistant")
render_global_sidebar()

def add_node_to_graph(dot, node, seen_set, net=None):
    # Neo4j 5 IDs have colons (e.g. 4:xxx), which confuse Graphviz ports. Sanitize them.
    safe_id = node.element_id.replace(":", "_")
    
    if safe_id in seen_set:
        return
    seen_set.add(safe_id)
    
    props = dict(node)
    label = list(node.labels)[0] if node.labels else "Node"
    
    # Try different name properties
    # Added: city (Locations), device_type (Devices)
    name = str(
        props.get("name") or 
        props.get("city") or 
        props.get("device_type") or 
        props.get("title") or 
        props.get("transaction_id") or 
        props.get("user_id") or 
        props.get("id") or 
        node.element_id
    )
    
    color = "lightblue"
    if label == "Transactions": color = "red"
    if label == "Users": 
        # Dynamic Risk Coloring
        risk = props.get("risk_score", 0)
        try:
            risk_val = float(risk)
        except:
            risk_val = 0
            
        if risk_val > 5:
            color = "#FF4B4B" # Bright Red (High Risk)
        elif risk_val > 2:
            color = "#FFA500" # Orange (Medium)
        else:
            color = "#90EE90" # Light Green (Safe)
            
    if label == "Locations": color = "orange"
    if label == "Devices": color = "violet"
    
    # Add to Graphviz
    dot.node(safe_id, label=f"{label}\n{name}", style="filled", fillcolor=color)

    # Add to PyVis
    if net:
        # Tooltip with all properties
        title_html = "<br>".join([f"<b>{k}:</b> {v}" for k,v in props.items()])
        net.add_node(safe_id, label=name, title=title_html, color=color, group=label)

def add_edge_to_graph(dot, rel, seen_set, net=None):
    safe_id = rel.element_id.replace(":", "_")
    if safe_id in seen_set:
        return
    seen_set.add(safe_id)
    
    start_safe = rel.start_node.element_id.replace(":", "_")
    end_safe = rel.end_node.element_id.replace(":", "_")
    
    # Add to Graphviz
    dot.edge(start_safe, end_safe, label=rel.type)

    # Add to PyVis
    if net:
        net.add_edge(start_safe, end_safe, title=rel.type)

st.set_page_config(page_title="Graph RAG Assistant", page_icon="🕸️", layout="wide")
st.title("🕸️ Graph RAG Assistant (Neo4j)")

# 1. State Init
if "graph_schema" not in st.session_state:
    st.session_state.graph_schema = None

# State Management for Graph Results
if "graph_rag_results" not in st.session_state:
    st.session_state.graph_rag_results = {
        "question": "",
        "cypher": "",
        "summary": "",
        "nodes": [],  # Processed nodes for vis
        "edges": [],  # Processed edges for vis
        "context_data": []
    }

# NEW: Bookmark storage
if "graph_bookmarks" not in st.session_state:
    st.session_state.graph_bookmarks = []  # list of {name, question, cypher}

# 2. Sidebar / Configuration
graph_llm_id = st.session_state.global_llm_id

with st.sidebar:
    if st.session_state.graph_schema:
        with st.expander("📊 Current Graph Schema", expanded=False):
            st.code(st.session_state.graph_schema, language="text")

# 3. Main Interface
col_left, col_right = st.columns([2, 1])

with col_right:
    # ── Bookmarked Queries Panel ───────────────────────────────────────────
    with st.expander("📌 Bookmarked Queries", expanded=bool(st.session_state.graph_bookmarks)):
        if not st.session_state.graph_bookmarks:
            st.caption("No bookmarks yet. Run a query, then click '📌 Bookmark' to save it.")
        else:
            for idx, bm in enumerate(st.session_state.graph_bookmarks):
                bm_col1, bm_col2 = st.columns([5, 1])
                bm_col1.markdown(f"**{bm['name']}**")
                bm_col1.caption(bm['question'][:80] + ("…" if len(bm['question']) > 80 else ""))
                if bm_col1.button("▶ Run", key=f"bm_run_{idx}", use_container_width=False):
                    st.session_state.selected_graph_q = bm["question"]
                    st.rerun()
                if bm_col2.button("🗑", key=f"bm_del_{idx}", help="Remove bookmark"):
                    st.session_state.graph_bookmarks.pop(idx)
                    st.rerun()
                st.divider()
            if st.button("🗑 Clear All Bookmarks", use_container_width=True):
                st.session_state.graph_bookmarks = []
                st.rerun()

    st.markdown("---")

    if st.button("🎲 Suggest Graph Questions", use_container_width=True, help="Automatically refreshes schema & generates suggestions"):
        with st.spinner("Analyzing Graph & Brainstorming..."):
            try:
                driver = settings.graph_driver
                with driver.session() as session:
                    # --- 1. Automatic Schema Refresh ---
                    res = session.run("CALL db.labels() YIELD label RETURN label")
                    labels = [r["label"] for r in res]
                    
                    schema_details = []
                    for label in labels:
                        prop_res = session.run(f"MATCH (n:`{label}`) RETURN n LIMIT 1")
                        record = prop_res.single()
                        if record:
                            node = record["n"]
                            props_str = ", ".join([f"{k} ({type(v).__name__})" for k, v in dict(node).items()])
                            schema_details.append(f"Label: {label}, Properties: [{props_str}]")
                        else:
                            schema_details.append(f"Label: {label}, Properties: []")

                    res_rels = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
                    rels = [r["relationshipType"] for r in res_rels]

                    res_patterns = session.run(
                        "MATCH (n)-[r]->(m) "
                        "WITH DISTINCT labels(n)[0] as start, type(r) as type, labels(m)[0] as end "
                        "RETURN start, type, end"
                    )
                    patterns = [f"({r['start']})-[:{r['type']}]->({r['end']})" for r in res_patterns]
                    
                    summary = (
                        "## Node Schemas\n" + "\n".join(schema_details) + 
                        "\n\n## Relationship Patterns\n" + (", ".join(patterns) if patterns else "No relationships found yet.") +
                        f"\n\n## Relationship Types: {rels}"
                    )
                    st.session_state.graph_schema = summary
                    
                    # --- 2. Suggest Questions ---
                    llm = init_llm(graph_llm_id)
                    prompt = (
                        "You are an expert in Graph Databases (Neo4j). Given the schema below, "
                        "suggest 9 interesting questions that can be answered by traversing the graph. "
                        "Focus on connections, paths, or clusters. "
                        "Questions should encourage returning paths ('p') or full nodes to see the network structure.\n\n"
                        f"Schema:\n{st.session_state.graph_schema}\n\n"
                        "Output ONLY 9 questions, one per line."
                    )
                    resp = llm.invoke(prompt)
                    questions = [line.strip("- 123. ") for line in resp.content.strip().split("\n") if line.strip()]
                    st.session_state.suggested_graph_questions = questions[:9]
                    st.success("Analysis complete! New questions suggested.")
            except Exception as e:
                st.error(f"Error during refresh/suggest: {e}")

with col_left:
    default_q = ""
    if "suggested_graph_questions" in st.session_state:
        # Display as a grid of buttons (e.g., 3 columns)
        st.write("Suggested Questions:")
        user_questions = st.session_state.suggested_graph_questions
        
        # Create 3 columns
        cols = st.columns(3)
        for i, q in enumerate(user_questions):
            col_idx = i % 3
            if cols[col_idx].button(f"Q{i+1}", help=q, key=f"gq_{i}", use_container_width=True):
                st.session_state.selected_graph_q = q
    
    st.markdown("### 🕵️ One-Click Analysis")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💍 Fraud Rings", help="Find users sharing devices/info"):
            st.session_state.selected_graph_q = (
                "Pattern: match p=(u1:Users)-[:LINKED_TO]-(t1:Transactions)-[:LINKED_TO]-(res)-[:LINKED_TO]-(t2:Transactions)-[:LINKED_TO]-(u2:Users) "
                "WHERE (res:Devices OR res:Locations) AND u1 <> u2. "
                "Return p showing these indirect connections."
            )
    with col_b:
        if st.button("🌟 Key Influencers", help="Find highly connected nodes"):
            st.session_state.selected_graph_q = (
                "Find 'Key Influencers': The top 10 Users or Devices with the most relationships (degree centrality). "
                "Structure: Use a UNION query. \n"
                "1. MATCH (u:Users) WITH u, COUNT { (u)--() } AS degree RETURN u AS node, 'User' AS type, u.name AS name, degree ORDER BY degree DESC LIMIT 5\n"
                "2. UNION\n"
                "3. MATCH (d:Devices) WITH d, COUNT { (d)--() } AS degree RETURN d AS node, 'Device' AS type, d.name AS name, degree ORDER BY degree DESC LIMIT 5\n"
                "CRITICAL: The columns ('node', 'type', 'name', 'degree') MUST be exactly the same in both subqueries. "
                "DO NOT add a global RETURN after the UNION. The query ends with the last subquery's RETURN."
            )
    
    if st.button("🚩 Risk Blast Radius", help="Find safe users connected to high-risk users", use_container_width=True):
        st.session_state.selected_graph_q = (
            "Find 'Risk Propagation': Identify 'High Risk' Users (risk_score > 5) and find ANY other Users connected to them "
            "via shared Devices or Locations (User-Transaction-Resource-Transaction-User). "
            "Return the paths showing how risk propagates to these neighbors. "
            "Pattern: MATCH p=(bad:Users)-[*4]-(neighbor:Users) WHERE bad.risk_score > 5 AND bad <> neighbor. "
            "Return p LIMIT 50."
        )

    st.markdown("### 🔗 Path Finder")
    with st.expander("Find connection between two Users"):
        # Fetch sample user IDs from DB for dropdowns
        try:
            if "user_id_list" not in st.session_state:
                with settings.graph_driver.session() as session:
                    res = session.run("MATCH (u:Users) RETURN u.user_id ORDER BY u.user_id LIMIT 50")
                    st.session_state.user_id_list = [r["u.user_id"] for r in res]
            
            user_options = st.session_state.user_id_list
        except Exception:
            user_options = []

        if user_options:
            col_src, col_tgt = st.columns(2)
            with col_src:
                uid_a = st.selectbox("Source User (A)", user_options, index=0)
            with col_tgt:
                uid_b = st.selectbox("Target User (B)", user_options, index=1 if len(user_options)>1 else 0)
        else:
            st.warning("Could not fetch user list. Please 'Refresh Graph Schema'.")
            col_src, col_tgt = st.columns(2)
            with col_src: uid_a = st.text_input("User A ID (e.g., 101)")
            with col_tgt: uid_b = st.text_input("User B ID (e.g., 102)")
        
        if st.button("Find Connection"):
            if uid_a and uid_b:
                if uid_a == uid_b:
                    st.warning("Please select different users.")
                else:
                    # UX Improvement: Pre-check connectivity
                    with st.spinner(f"Checking connectivity between {uid_a} and {uid_b}..."):
                        has_path = False
                        try:
                            with settings.graph_driver.session() as session:
                                # Quick check for ANY path (breadth-first)
                                check_q = (
                                    f"MATCH (u1:Users {{user_id: {uid_a}}}), (u2:Users {{user_id: {uid_b}}}) "
                                    "MATCH p=shortestPath((u1)-[*..10]-(u2)) "
                                    "RETURN length(p) LIMIT 1"
                                )
                                if session.run(check_q).single():
                                    has_path = True
                        except Exception as e:
                            logger.error(f"Connectivity check failed: {e}")
                            # Fallback to letting the main query run if check errors out
                            has_path = True 

                    if has_path:
                        st.session_state.selected_graph_q = (
                            f"Find the shortest path between User {uid_a} and User {uid_b}. "
                            "Use the Cypher 'shortestPath' function with variable length relationships. "
                            "Pattern: MATCH p=shortestPath((u1:Users)-[:LINKED_TO*]-(u2:Users)). "
                            "Match users by 'user_id' property (treat as Integer). "
                            "Return the path 'p'."
                        )
                    else:
                        st.error(f"❌ No path found between User {uid_a} and User {uid_b}. Try another pair.")
            else:
                st.warning("Please enter both User IDs.")

    with st.expander("Find Lookalikes (Similarity/Clones)"):
        # reuse user_options if available
        user_options_lookalike = st.session_state.get("user_id_list", [])
        if user_options_lookalike:
            target_uid = st.selectbox("Select User to Analyze", user_options_lookalike, key="lookalike_target")
        else:
            target_uid = st.text_input("Enter User ID", key="lookalike_target_txt")

        if st.button("Scan for Clones"):
            if target_uid:
                st.session_state.selected_graph_q = (
                    f"Find 'Lookalike' users for User {target_uid}. "
                    "Logic: First, find top 5 Users sharing the most 'Devices' or 'Locations' using WITH. "
                    "Then, match the paths between the original user and these top candidates. "
                    "Structure: MATCH (u1:Users {user_id: " + str(target_uid) + "})-[*2]-(r)-[*2]-(u2:Users) "
                    "WHERE u1 <> u2 WITH u1, u2, count(DISTINCT r) as overlap ORDER BY overlap DESC LIMIT 5 "
                    "MATCH p=(u1)-[*2]-(r)-[*2]-(u2) RETURN p, overlap, u2.user_id "
                )
            else:
                st.warning("Please select a user.")
    
    if "selected_graph_q" in st.session_state:
        default_q = st.session_state.selected_graph_q

    question = st.text_area("Ask a question about relationships/network:", value=default_q, height=100)

run_investigation = st.button("🚀 Run Graph Query")
if run_investigation:
    if not question:
        st.warning("Please ask a question.")
        st.stop()

    max_retries = 3
    current_attempt = 0
    cypher = ""
    last_error = ""
    
    # Initialize vis and context data
    nodes_data = []
    edges_data = []
    node_ids = set()
    edge_ids = set()
    context_data = []

    def collect_node(node):
        eid = node.element_id
        if eid in node_ids: return
        node_ids.add(eid)
        props = dict(node)
        label = list(node.labels)[0] if node.labels else "Node"
        name = str(props.get("name") or props.get("city") or props.get("device_type") or props.get("title") or props.get("transaction_id") or props.get("user_id") or props.get("id") or eid)
        nodes_data.append({"id": eid, "label": label, "name": name, "props": props})

    def collect_edge(rel):
        eid = rel.element_id
        if eid in edge_ids: return
        edge_ids.add(eid)
        edges_data.append({
            "id": eid,
            "type": rel.type,
            "from": rel.start_node.element_id,
            "to": rel.end_node.element_id,
            "props": dict(rel)
        })

    def deep_collect(item):
        if item is None: return
        if isinstance(item, list):
            for sub in item: deep_collect(sub)
        elif isinstance(item, dict):
            for sub in item.values(): deep_collect(sub)
        elif hasattr(item, "nodes") and hasattr(item, "relationships"): # Path
            for n in item.nodes: collect_node(n)
            for r in item.relationships: collect_edge(r)
        elif hasattr(item, "labels"): # Node
            collect_node(item)
        elif hasattr(item, "type"): # Relationship
            collect_edge(item)

    # 1. Self-Repair Loop for Cypher
    success = False
    while current_attempt < max_retries:
        current_attempt += 1
        with st.spinner(f"Investigation Attempt {current_attempt}/{max_retries}..." if current_attempt > 1 else "Analyzing Graph Relationships..."):
            try:
                from agents.cypher_recovery_agent import generate_repaired_cypher, validate_cypher_safety
                
                schema_context = st.session_state.graph_schema or "Labels: Users, Transactions, Devices, Locations"

                cypher = generate_repaired_cypher(
                    question=question,
                    last_cypher=None,
                    last_error=last_error,
                    schema_context=schema_context,
                    llm_id=graph_llm_id
                )
                st.toast(f"Generated Cypher: {cypher[:50]}...", icon="🔍")

                # Pre-execution Safety Check
                safety_error = validate_cypher_safety(cypher)
                if safety_error:
                    last_error = safety_error
                    st.toast(f"Safety check failed: {safety_error}", icon="⚠️")
                    continue

                # Execute and Collect
                driver = settings.graph_driver
                logger.info(f"--- GRAPH RAG EXECUTING CYPHER ---\n{cypher}\n--------------------------------------")
                with driver.session() as session:
                    result = session.run(cypher)
                    # Clear placeholders for this attempt
                    nodes_data, edges_data, node_ids, edge_ids, context_data = [], [], set(), set(), []
                    
                    found_any = False
                    for record in result:
                        found_any = True
                        # Collect for context (summary)
                        rec_dict = {}
                        for k, v in record.items():
                            if hasattr(v, "element_id"):
                                d = dict(v); d["_id"] = v.element_id
                                if hasattr(v, "labels"): d["_labels"] = list(v.labels)
                                if hasattr(v, "type"): 
                                    d["_type"] = v.type
                                    d["_start"] = v.start_node.element_id
                                    d["_end"] = v.end_node.element_id
                                rec_dict[k] = d
                            else: rec_dict[k] = v
                        context_data.append(rec_dict)
                        # Collect for visualization
                        for val in record.values(): deep_collect(val)
                    
                    if not found_any:
                        last_error = "Query returned no results. Try a broader pattern."
                        continue
                    
                    # Store results on success
                    st.session_state.graph_rag_results["question"] = question
                    st.session_state.graph_rag_results["cypher"] = cypher
                    st.session_state.graph_rag_results["nodes"] = nodes_data
                    st.session_state.graph_rag_results["edges"] = edges_data
                    st.session_state.graph_rag_results["context_data"] = context_data
                    success = True
                    st.toast(f"Query successful! Found {len(nodes_data)} nodes.", icon="✅")
                    break

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Graph RAG Attempt {current_attempt} failed: {e}")
                if current_attempt == max_retries:
                    st.error(f"Investigation failed after {max_retries} attempts: {e}")
                    st.stop()
        
        if not success and current_attempt >= max_retries:
            st.error(f"❌ No results found after {max_retries} attempts. The graph might be empty or the pattern too specific. Try rebuilding the graph in the Admin Console.")
            st.stop()

    # 2. Final Summary Generation (Outside loop, only if success)
    if success:
        with st.spinner("Synthesizing Final Report..."):
            try:
                llm = init_llm(graph_llm_id)
                context_str = str(context_data[:50])
                summary_prompt = (
                    "You are a Senior Fraud Analyst. Analyze the relationship graph results below.\n"
                    f"Question: {question}\n"
                    f"Results: {context_str}\n\n"
                    "Format as Markdown report with Findings, Risk Assessment (Score 1-10), and Recommended Actions."
                )
                summary_resp = llm.invoke(summary_prompt)
                st.session_state.graph_rag_results["summary"] = summary_resp.content
            except Exception as e:
                st.warning(f"Could not generate summary: {e}")
                st.session_state.graph_rag_results["summary"] = "Data retrieved successfully, but summary generation failed."

# --- RENDERING SECTION ---
res = st.session_state.graph_rag_results
if res["cypher"]:
    st.markdown("---")
    st.header("🕸️ Graph Investigation Findings")
    st.code(res["cypher"], language="cypher")

    # ── Bookmark this Query ────────────────────────────────────────────────
    bm_c1, bm_c2 = st.columns([3, 1])
    bm_name = bm_c1.text_input(
        "Bookmark name:", value=res["question"][:50],
        label_visibility="collapsed", placeholder="Give this query a name…",
        key="bm_name_input"
    )
    if bm_c2.button("📌 Bookmark", use_container_width=True):
        already = any(b["cypher"] == res["cypher"] for b in st.session_state.graph_bookmarks)
        if already:
            st.info("This query is already bookmarked.")
        else:
            st.session_state.graph_bookmarks.append({
                "name": bm_name or res["question"][:50],
                "question": res["question"],
                "cypher": res["cypher"]
            })
            st.toast("Query bookmarked! ✅", icon="📌")
    
    if res["nodes"]:
        import graphviz
        from pyvis.network import Network
        import streamlit.components.v1 as components
        import tempfile
        from collections import Counter

        # ── Result Stats Bar ──────────────────────────────────────────────────
        st.markdown("---")
        node_type_counts = Counter(n["label"] for n in res["nodes"])
        edge_type_counts = Counter(e["type"]  for e in res["edges"])
        all_counts = list(node_type_counts.items()) + list(edge_type_counts.items())
        n_cols = min(len(all_counts), 6)
        if n_cols > 0:
            stat_cols = st.columns(n_cols)
            for i, (lbl, cnt) in enumerate(all_counts[:n_cols]):
                icon = "🔵" if lbl in node_type_counts else "🔗"
                stat_cols[i].metric(f"{icon} {lbl}", cnt)
        st.caption(
            f"**{len(res['nodes'])} nodes** across {len(node_type_counts)} type(s)  ·  "
            f"**{len(res['edges'])} relationships** across {len(edge_type_counts)} type(s)"
        )
        st.markdown("---")
        
        # Build visualizations from processed data
        dot = graphviz.Digraph(comment='Query Result')
        dot.attr(rankdir='LR')
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        net.force_atlas_2based()
        
        # Apply coloring and naming
        for n in res["nodes"]:
            eid_safe = n["id"].replace(":", "_")
            label = n["label"]
            name = n["name"]
            props = n["props"]
            
            color = "lightblue"
            if label == "Transactions": color = "red"
            elif label == "Users":
                risk = float(props.get("risk_score", 0))
                color = "#FF4B4B" if risk > 5 else ("#FFA500" if risk > 2 else "#90EE90")
            elif label == "Locations": color = "orange"
            elif label == "Devices": color = "violet"
            
            dot.node(eid_safe, label=f"{label}\n{name}", style="filled", fillcolor=color)
            title_html = "<br>".join([f"<b>{k}:</b> {v}" for k,v in props.items()])
            net.add_node(eid_safe, label=name, title=title_html, color=color, group=label)
            
        for e in res["edges"]:
            start_safe = e["from"].replace(":", "_")
            end_safe = e["to"].replace(":", "_")
            dot.edge(start_safe, end_safe, label=e["type"])
            net.add_edge(start_safe, end_safe, title=e["type"])

        st.success(f"Graph Analysis Complete.")
        v_col1, v_col2 = st.columns([3, 2])
        with v_col1:
            st.subheader("🕸️ Interactive Graph")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                with open(tmp.name, 'r', encoding='utf-8') as f:
                    html = f.read()
                components.html(html, height=600, scrolling=True)
            
        with v_col2:
            st.subheader("🖼️ Static Chart")
            st.graphviz_chart(dot)
            st.divider()
            if st.button("Generate PDF Report"):
                with st.spinner("Forging Report..."):
                    try:
                        import os
                        # Ensure output directories exist
                        os.makedirs(os.path.join("data", "generated"), exist_ok=True)
                        
                        # Re-render Graphviz to PNG for PDF
                        img_path = os.path.join("data", "generated", "temp_graph")
                        dot.render(img_path, format="png", cleanup=True)
                        
                        output_path = os.path.join("data", "generated", "Fraud_Analysis_Report.pdf")
                        final_pdf = create_report(
                            question=res["question"],
                            summary_text=res["summary"],
                            image_path=img_path + ".png",
                            output_path=output_path
                        )
                        with open(final_pdf, "rb") as f:
                            st.download_button("⬇ Download PDF Analysis", f, "Fraud_Analysis_Report.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"PDF Error: {e}")
    else:
        st.info("Query returned no graph objects (nodes/edges). Review the summary below.")
        with st.expander("🛠️ Admin Debug: Raw Records (First 5)"):
            st.json(res["context_data"][:5])

    st.divider()
    st.subheader("🤖 AI Summary")
    st.markdown(res["summary"])
else:
    st.info("Start a graph investigation by running the query above.")


