from fastapi import APIRouter, Depends, HTTPException, Body
from api.dependencies import requires_admin, get_current_user
import logging
import sqlite3
from pathlib import Path
from config.settings import settings
from typing import List, Any
from utils.auth_utils import get_password_hash

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/clean-db", dependencies=[Depends(requires_admin)])
async def clean_db():
    """Delete all tables in the SQLite database (or remove the DB file) and clean up generated schema documentation."""
    db_path = settings.db_path_obj
    docs_dir = settings.docs_dir_obj
    try:
        # Remove the SQLite database file
        if db_path.exists():
            db_path.unlink()
            logger.info(f"Database file {db_path} removed")
        # Recreate empty DB file (will be created on next ingestion)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.touch()
        # Delete individual schema markdown files
        for md_file in docs_dir.glob("schema_*.md"):
            md_file.unlink(missing_ok=True)
            logger.info(f"Deleted schema markdown {md_file}")
        # Clear the central schema reference file
        reference_path = docs_dir / "database_schema_reference.md"
        if reference_path.exists():
            reference_path.write_text("# Database Schema Reference\n\n_No schemas available._\n", encoding="utf-8")
            logger.info(f"Cleared central schema reference {reference_path}")
        return {"detail": "Database cleaned"}
    except Exception as e:
        logger.error(f"Failed to clean database: {e}")
        raise HTTPException(status_code=500, detail="Failed to clean database")

@router.post("/delete-uploads", dependencies=[Depends(requires_admin)])
def delete_uploads():
    """Delete all user‑uploaded files."""
    try:
        # Delete files in uploads directory
        uploads_dir = settings.uploads_dir_obj
        if uploads_dir.exists():
            for file in uploads_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        
        # Delete schema docs in docs/ (schema_*.md)
        docs_dir = settings.docs_dir_obj
        if docs_dir.exists():
            for file in docs_dir.glob("schema_*.md"):
                file.unlink()
            
            # Also clear the central reference file
            ref_file = docs_dir / "database_schema_reference.md"
            if ref_file.exists():
                 ref_file.write_text("# Database Schema Reference\n\nNo schemas available.", encoding="utf-8")

        logger.info("Deleted all uploads and schema markdown files")
        return {"message": "All uploaded files and schemas deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-graph", dependencies=[Depends(requires_admin)])
def rebuild_graph():
    """Rebuild the graph store from uploaded files."""
    try:
        from rag_sql.file_loader import extract_text_from_file
        from rag_sql.graph_utils import create_document_node
        
        # 1. Clear existing graph
        # Note: This is a nuclear option for the graph content
        driver = settings.graph_driver
        with driver.session() as session:
            session.run("MATCH (n:Document) DETACH DELETE n")
        logger.info("Cleared existing Document nodes from graph")

        # 2. Iterate uploads and re-ingest (Source of Truth)
        uploads_dir = settings.uploads_dir_obj
        count = 0
        
        # Track processed names to avoid redundant work if needed, 
        # but merging is safe.
        
        if uploads_dir.exists():
            for file_path in uploads_dir.glob("*"):
                if file_path.is_file():
                    try:
                        text_content, file_ext = extract_text_from_file(file_path)
                        if text_content:
                            create_document_node(
                                name=file_path.stem, 
                                content=text_content, 
                                doc_type=file_ext
                            )
                            count += 1
                    except Exception as e:
                        logger.error(f"Failed to re-ingest {file_path.name} from uploads: {e}")
        
        # 3. Iterate docs/ directory (Schema docs, manual docs)
        docs_dir = settings.docs_dir_obj
        if docs_dir.exists():
            for file_path in docs_dir.glob("*.md"):
                try:
                    text_content, file_ext = extract_text_from_file(file_path)
                    if text_content:
                         create_document_node(
                            name=file_path.stem, 
                            content=text_content, 
                            doc_type=file_ext
                        )
                         count += 1
                except Exception as e:
                    logger.error(f"Failed to re-ingest {file_path.name} from docs: {e}")

        # 4. Sync Database Schema Graph (Tables/Relationships)
        from rag_sql.graph_utils import sync_db_schema_to_graph
        sync_db_schema_to_graph()
        logger.info("Synced SQLite schema to Graph Store")

        # 5. Project actual data rows to Neo4j
        from rag_sql.graph_data_projector import project_sqlite_to_neo4j
        projection_res = project_sqlite_to_neo4j()
        if projection_res.get("status") == "success":
            stats = projection_res.get("stats", {})
            logger.info(f"Projected data to Graph Store: {stats}")
        else:
            logger.warning(f"Data projection warning: {projection_res.get('message')}")

        # 6. Rebuild Vector Store
        from rag_sql.build_kb_index import build_vectorstore
        kb_dir = settings.kb_dir_obj
        docs_dir = settings.docs_dir_obj
        from rag_sql.build_kb_index import build_vectorstore
        kb_dir = settings.kb_dir_obj
        docs_dir = settings.docs_dir_obj
        build_vectorstore(docs_dir=docs_dir, out_dir=kb_dir)

        logger.info(f"Graph rebuild complete. Processed {count} files.")
        return {"message": f"Graph rebuilt successfully. Processed {count} files."}

    except Exception as e:
        logger.error(f"Error rebuilding graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete-graph", dependencies=[Depends(requires_admin)])
def delete_graph():
    """Delete all nodes and relationships from the graph store."""
    try:
        driver = settings.graph_driver
        with driver.session() as session:
            # Nuclear option: Delete everything
            session.run("MATCH (n) DETACH DELETE n")
            
        logger.info("Deleted all nodes/relationships from graph store via admin action")
        return {"message": "Graph store cleaned successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph-data")
def get_graph_data():
    """Fetch nodes and relationships for visualization."""
    import math
    
    def clean_props(props):
        """Clean properties for JSON compliance (handle NaN, Inf)."""
        if not isinstance(props, dict):
            return props
        cleaned = {}
        for k, v in props.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                cleaned[k] = None
            else:
                cleaned[k] = v
        return cleaned

    try:
        driver = settings.graph_driver
        nodes = []
        edges = []
        
        with driver.session() as session:
            # Fetch all nodes
            # LIMIT to avoid crashing browser with too many nodes
            result = session.run("MATCH (n) RETURN n LIMIT 1000")
            for record in result:
                node = record["n"]
                props = dict(node)
                label = list(node.labels)[0] if node.labels else "Node"
                
                # Use a specific property for label if available (name, title, id)
                name = props.get("name") or props.get("title") or props.get("id") or f"{label}_{node.element_id}"
                
                nodes.append({
                    "id": node.element_id,
                    "label": str(name),
                    "group": label,
                    "properties": clean_props(props)
                })

            # Fetch all relationships
            result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 2000")
            for record in result:
                start = record["n"]
                end = record["m"]
                rel = record["r"]
                
                edges.append({
                    "source": start.element_id,
                    "target": end.element_id,
                    "label": rel.type,
                    "properties": clean_props(dict(rel))
                })

        return {"nodes": nodes, "edges": edges}
        
    except Exception as e:
        logger.error(f"Error fetching graph data: {e}")
        # Friendlier error for common connection issues
        error_msg = str(e)
        if "Name or service not known" in error_msg or "ServiceUnavailable" in error_msg:
             error_msg = "Neo4j Graph Store is currently unavailable. Please ensure the 'fraud_neo4j' container is running and healthy."
        elif "Unauthorized" in error_msg or "AuthError" in error_msg:
             error_msg = "Authentication failed for Neo4j Graph Store. Please check your credentials."
             
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/graph-evaluation")
def get_graph_evaluation():
    """Comprehensive graph database evaluation: health, performance, and quality."""
    import time
    import math

    def ts():
        return time.monotonic()

    result = {
        "health": {},
        "performance": {},
        "quality": {},
        "retrieval": {},
        "summary": {}
    }

    try:
        driver = settings.graph_driver

        # -------------------------
        # 1. INFRASTRUCTURE HEALTH
        # -------------------------
        health = {}

        # Ping / connectivity
        t0 = ts()
        try:
            with driver.session() as session:
                session.run("RETURN 1")
            health["bolt_connectivity"] = {"status": "ok", "latency_ms": round((ts() - t0) * 1000, 2)}
        except Exception as e:
            health["bolt_connectivity"] = {"status": "error", "detail": str(e)}

        # Server info
        try:
            with driver.session() as session:
                info = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition").data()
            health["server_info"] = info[0] if info else {}
        except Exception:
            health["server_info"] = {}

        # Store sizes / node counts by label
        try:
            with driver.session() as session:
                label_counts = session.run(
                    "CALL apoc.meta.stats() YIELD labels RETURN labels"
                ).data()
            if label_counts:
                health["label_distribution"] = label_counts[0].get("labels", {})
        except Exception:
            # Fallback without APOC
            try:
                with driver.session() as session:
                    lc = session.run("MATCH (n) RETURN labels(n) AS lbl, count(*) AS cnt").data()
                health["label_distribution"] = {
                    (r["lbl"][0] if r["lbl"] else "Unknown"): r["cnt"] for r in lc
                }
            except Exception as e2:
                health["label_distribution"] = {"error": str(e2)}

        # Relationship type distribution
        try:
            with driver.session() as session:
                rel_dist = session.run(
                    "MATCH ()-[r]->() RETURN type(r) AS rtype, count(*) AS cnt ORDER BY cnt DESC"
                ).data()
            health["relationship_distribution"] = {r["rtype"]: r["cnt"] for r in rel_dist}
        except Exception as e:
            health["relationship_distribution"] = {"error": str(e)}

        result["health"] = health

        # -------------------------
        # 2. QUERY PERFORMANCE PROFILING
        # -------------------------
        perf = {}

        queries_to_profile = [
            ("total_nodes", "MATCH (n) RETURN count(n) AS cnt"),
            ("total_relationships", "MATCH ()-[r]->() RETURN count(r) AS cnt"),
            ("avg_degree", "MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN round(avg(count(r)), 2) AS avg_deg"),
            ("max_connections", "MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN n, count(r) AS deg ORDER BY deg DESC LIMIT 1"),
        ]

        for query_name, cypher in queries_to_profile:
            t0 = ts()
            try:
                with driver.session() as session:
                    res = session.run(cypher).data()
                elapsed_ms = round((ts() - t0) * 1000, 2)
                first = res[0] if res else {}
                perf[query_name] = {
                    "latency_ms": elapsed_ms,
                    "result": {k: (None if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else v)
                               for k, v in first.items()},
                    "status": "ok"
                }
            except Exception as e:
                perf[query_name] = {"latency_ms": None, "status": "error", "detail": str(e)}

        result["performance"] = perf

        # -------------------------
        # 3. GRAPH QUALITY METRICS
        # -------------------------
        quality = {}

        # Orphaned nodes (no relationships)
        try:
            with driver.session() as session:
                orphans = session.run(
                    "MATCH (n) WHERE NOT (n)--() RETURN count(n) AS cnt"
                ).single()
            quality["orphaned_nodes"] = int(orphans["cnt"]) if orphans else 0
        except Exception as e:
            quality["orphaned_nodes"] = {"error": str(e)}

        # Density: edges / (nodes*(nodes-1))
        try:
            with driver.session() as session:
                counts = session.run(
                    "MATCH (n) WITH count(n) AS n_count MATCH ()-[r]->() RETURN n_count, count(r) AS e_count"
                ).data()
            if counts:
                n = counts[0].get("n_count", 0)
                e = counts[0].get("e_count", 0)
                density = round(e / (n * (n - 1)), 6) if n > 1 else 0.0
                quality["graph_density"] = density
                quality["total_nodes"] = n
                quality["total_edges"] = e
        except Exception as e:
            quality["graph_density"] = {"error": str(e)}

        # Nodes missing key properties
        try:
            with driver.session() as session:
                missing = session.run(
                    "MATCH (n) WHERE n.name IS NULL AND n.title IS NULL AND n.id IS NULL RETURN count(n) AS cnt"
                ).single()
            quality["nodes_missing_label_property"] = int(missing["cnt"]) if missing else 0
        except Exception as e:
            quality["nodes_missing_label_property"] = {"error": str(e)}

        # Duplicate node check (same name, same label)
        try:
            with driver.session() as session:
                dups = session.run(
                    "MATCH (n) WHERE n.name IS NOT NULL "
                    "WITH labels(n) AS lbl, n.name AS nm, count(*) AS cnt "
                    "WHERE cnt > 1 RETURN sum(cnt - 1) AS duplicate_count"
                ).single()
            quality["duplicate_nodes_estimate"] = int(dups["duplicate_count"]) if dups and dups["duplicate_count"] else 0
        except Exception as e:
            quality["duplicate_nodes_estimate"] = {"error": str(e)}

        result["quality"] = quality

        # -------------------------
        # 4. RETRIEVAL QUALITY ASSESSMENT
        # -------------------------
        retrieval = {}

        # Sample traversal: find connected components depth-2
        try:
            t0 = ts()
            with driver.session() as session:
                sample = session.run(
                    "MATCH path = (n)-[*1..2]->(m) "
                    "RETURN count(path) AS reachable_pairs, avg(length(path)) AS avg_path_len LIMIT 1"
                ).data()
            elapsed_ms = round((ts() - t0) * 1000, 2)
            first = sample[0] if sample else {}
            retrieval["depth2_reachability"] = {
                "reachable_pairs": first.get("reachable_pairs", 0),
                "avg_path_length": round(first.get("avg_path_len") or 0, 3),
                "latency_ms": elapsed_ms
            }
        except Exception as e:
            retrieval["depth2_reachability"] = {"error": str(e)}

        # Keyword search simulation (checks if text search is feasible)
        try:
            t0 = ts()
            with driver.session() as session:
                kw_res = session.run(
                    "MATCH (n) WHERE toLower(toString(n.name)) CONTAINS 'fraud' "
                    "RETURN count(n) AS matches LIMIT 1"
                ).data()
            elapsed_ms = round((ts() - t0) * 1000, 2)
            retrieval["keyword_search_fraud"] = {
                "matches": kw_res[0].get("matches", 0) if kw_res else 0,
                "latency_ms": elapsed_ms
            }
        except Exception as e:
            retrieval["keyword_search_fraud"] = {"error": str(e)}

        # Relationship coverage: % of nodes that have at least one relationship
        try:
            with driver.session() as session:
                cov = session.run(
                    "MATCH (n) OPTIONAL MATCH (n)-[r]-() "
                    "RETURN count(n) AS total, count(r) AS connected"
                ).data()
            if cov:
                total = cov[0].get("total", 0)
                connected = cov[0].get("connected", 0)
                coverage = round(connected / total * 100, 1) if total > 0 else 0
                retrieval["node_connectivity_coverage_pct"] = coverage
        except Exception as e:
            retrieval["node_connectivity_coverage_pct"] = {"error": str(e)}

        result["retrieval"] = retrieval

        # -------------------------
        # 5. SUMMARY / GRADE
        # -------------------------
        issues = []
        score = 100

        if health.get("bolt_connectivity", {}).get("status") != "ok":
            issues.append("Neo4j connectivity is down.")
            score -= 40

        orphaned = quality.get("orphaned_nodes", 0)
        if isinstance(orphaned, int) and orphaned > 10:
            issues.append(f"{orphaned} orphaned nodes with no relationships detected.")
            score -= 10

        missing_props = quality.get("nodes_missing_label_property", 0)
        if isinstance(missing_props, int) and missing_props > 5:
            issues.append(f"{missing_props} nodes are missing name/title/id properties.")
            score -= 5

        dups = quality.get("duplicate_nodes_estimate", 0)
        if isinstance(dups, int) and dups > 0:
            issues.append(f"~{dups} potential duplicate nodes detected.")
            score -= 5

        bolt_latency = health.get("bolt_connectivity", {}).get("latency_ms")
        if bolt_latency and bolt_latency > 500:
            issues.append(f"High Neo4j latency: {bolt_latency}ms (ideal <100ms).")
            score -= 10

        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        result["summary"] = {
            "score": max(score, 0),
            "grade": grade,
            "issues": issues if issues else ["No major issues detected. Graph store is healthy."]
        }

        return result

    except Exception as e:
        logger.error(f"Error running graph evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project-data-to-graph", dependencies=[Depends(requires_admin)])
def project_data_to_graph():
    """
    Project actual table data (rows) from SQLite to Neo4j.
    """
    try:
        from rag_sql.graph_data_projector import project_sqlite_to_neo4j
        result = project_sqlite_to_neo4j()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
            
        return result
    except Exception as e:
        logger.error(f"Error projecting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", dependencies=[Depends(requires_admin)])
async def list_users():
    """List all registered users."""
    try:
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, role, created_at FROM app_users")
            users = [dict(row) for row in cursor.fetchall()]
        return {"users": users}
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@router.patch("/users/{user_id}", dependencies=[Depends(requires_admin)])
async def update_user_role(user_id: int, role: str = Body(..., embed=True)):
    """Update a user's role."""
    try:
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 1. Validate role exists
            cursor.execute("SELECT name FROM app_roles WHERE name = ?", (role,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Invalid role: {role}. Please create it first in Role Management.")
            
            # 2. Update user
            cursor.execute("UPDATE app_users SET role = ? WHERE id = ?", (role, user_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
        return {"message": f"User {user_id} role updated to {role}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user role")

@router.patch("/users/{user_id}/username", dependencies=[Depends(requires_admin)])
async def update_username(user_id: int, username: str = Body(..., embed=True)):
    """Update a user's username."""
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
        
    try:
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE app_users SET username = ? WHERE id = ?", (username, user_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
        return {"message": f"User {user_id} renamed to {username}"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already taken")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update username: {e}")
        raise HTTPException(status_code=500, detail="Failed to update username")

@router.patch("/users/{user_id}/email", dependencies=[Depends(requires_admin)])
async def update_user_email(user_id: int, email: str = Body(..., embed=True)):
    """Update a user's email."""
    # Basic validation
    if email and "@" not in email:
         raise HTTPException(status_code=400, detail="Invalid email format")
         
    try:
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE app_users SET email = ? WHERE id = ?", (email, user_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
        return {"message": f"User {user_id} email updated"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already used by another user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update email: {e}")
        raise HTTPException(status_code=500, detail="Failed to update email")

@router.patch("/users/{user_id}/password", dependencies=[Depends(requires_admin)])
async def update_password(user_id: int, password: str = Body(..., embed=True)):
    """Update a user's password."""
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
    try:
        hashed_pw = get_password_hash(password)
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE app_users SET hashed_password = ? WHERE id = ?", (hashed_pw, user_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
        return {"message": f"User {user_id} password updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update password: {e}")
        raise HTTPException(status_code=500, detail="Failed to update password")

@router.delete("/users/{user_id}", dependencies=[Depends(requires_admin)])
async def delete_user(user_id: int):
    """Delete a user."""
    try:
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM app_users WHERE id = ?", (user_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
        return {"message": f"User {user_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.get("/permissions")
async def get_permissions(current_user: dict = Depends(get_current_user)):
    """Get permissions for the current user's role."""
    role_name = current_user.get("role", "guest")
    logger.info(f"Fetching permissions for role: {role_name}")
    try:
        import json
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT permissions FROM app_roles WHERE name = ?", (role_name,))
            row = cursor.fetchone()
            if row:
                perms = json.loads(row["permissions"])
                logger.info(f"Returning {len(perms)} permissions for {role_name}")
                return {"role": role_name, "permissions": perms}
            logger.warning(f"No permissions found in DB for role: {role_name}")
            return {"role": role_name, "permissions": []}
    except Exception as e:
        logger.error(f"Failed to fetch permissions for {role_name}: {e}")
        return {"role": role_name, "permissions": []}

@router.get("/roles", dependencies=[Depends(requires_admin)])
async def list_roles():
    """List all available roles and their permissions."""
    try:
        import json
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name, permissions FROM app_roles")
            roles = []
            for row in cursor.fetchall():
                try:
                    roles.append({"name": row["name"], "permissions": json.loads(row["permissions"])})
                except:
                    roles.append({"name": row["name"], "permissions": []})
        return {"roles": roles}
    except Exception as e:
        logger.error(f"Failed to list roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roles", dependencies=[Depends(requires_admin)])
async def create_or_update_role(name: str = Body(...), permissions: List[str] = Body(...)):
    """Create or update a role and its permissions."""
    import json
    perms_json = json.dumps(permissions)
    try:
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO app_roles (name, permissions) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET permissions = excluded.permissions",
                (name, perms_json)
            )
            conn.commit()
        return {"message": f"Role '{name}' updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/roles/{name}", dependencies=[Depends(requires_admin)])
async def delete_role(name: str):
    """Delete a role."""
    if name in ["admin", "guest"]:
        raise HTTPException(status_code=400, detail="Cannot delete system roles: 'admin' or 'guest'")
    try:
        with sqlite3.connect(settings.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM app_roles WHERE name = ?", (name,))
            conn.commit()
        return {"message": f"Role '{name}' deleted"}
    except Exception as e:
        logger.error(f"Failed to delete role: {e}")
        raise HTTPException(status_code=500, detail=str(e))
