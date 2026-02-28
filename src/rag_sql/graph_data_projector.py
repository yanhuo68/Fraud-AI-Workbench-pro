import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from config.settings import settings

logger = logging.getLogger(__name__)

def project_sqlite_to_neo4j(db_path: Path = None):
    """
    Project actual data rows from SQLite tables into Neo4j nodes and relationships.
    """
    if db_path is None:
        db_path = settings.db_path_obj

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return {"status": "error", "message": "Database not found"}

    driver = settings.graph_driver
    stats = {"nodes_created": 0, "relationships_created": 0}

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cursor.fetchall()]
            
            logger.info(f"Starting data projection for tables: {tables}")

            # 2. Iterate tables and create Nodes
            with driver.session() as session:
                for table in tables:
                    # Read table data
                    df = pd.read_sql_query(f"SELECT * FROM \"{table}\"", conn)
                    # Handle NaN values to ensure JSON compliance
                    df = df.where(pd.notnull(df), None)
                    rows = df.to_dict('records')
                    
                    if not rows:
                        continue
                        
                    logger.info(f"Projecting {len(rows)} rows for table '{table}'...")
                    
                    # Batch processing to avoid huge transactions
                    batch_size = 1000
                    for i in range(0, len(rows), batch_size):
                        batch = rows[i:i+batch_size]
                        
                        # Clean batch data for Neo4j (dates to strings, etc)
                        # Neo4j python driver handles standard types well
                        
                        # Cypher query to unwind batch and merge nodes
                        # We assume every table has a Primary Key or we use full row matching
                        # For simplicity in this projection, we use a generated ID if PK is tricky,
                        # but ideally we use the PK.
                        
                        # Let's detect PK if possible, strictly we need it for MERGE uniqueness
                        # If no unique PK, we might create duplicates if we run this multiple times
                        # Strategy: Use row content hash or trust MERGE on all props (slow)
                        # Better Strategy: Introspect PK.
                        
                        pk = get_primary_key(cursor, table)
                        
                        if pk:
                            # Merge using PK
                            cypher = (
                                f"UNWIND $batch AS row "
                                f"MERGE (n:`{table}` {{ `{pk}`: row.`{pk}` }}) "
                                f"SET n += row"
                            )
                        else:
                            # No PK, just create (idempotency issues here, skipping MERGE)
                            # Or we can generate a hash.
                            # Fallback: CREATE
                            cypher = (
                                f"UNWIND $batch AS row "
                                f"CREATE (n:`{table}`) "
                                f"SET n = row"
                            )
                            
                        session.run(cypher, batch=batch)
                        stats["nodes_created"] += len(batch)

            # 3. Create Relationships (Foreign Keys)
            logger.info("Projecting relationships...")
            with driver.session() as session:
                for table in tables:
                    cursor.execute(f"PRAGMA foreign_key_list('{table}')")
                    fks = cursor.fetchall()
                    # id, seq, table, from, to, ...
                    
                    for fk in fks:
                        target_table = fk[2]
                        from_col = fk[3]
                        to_col = fk[4]
                        
                        logger.info(f"Linking {table}.{from_col} -> {target_table}.{to_col}")
                        
                        # Run relationship creation
                        # MATCH (a:Source), (b:Target) WHERE a.fk = b.pk MERGE (a)-[:LINKED_TO]->(b)
                        # We do this in batches if possible, or single large query if data size allows
                        # For safety, we run it as a single atomic query per FK relationship type
                        
                        # Use robust matching (toString) to avoid int vs string type mismatches
                        cypher_rel = (
                            f"MATCH (source:`{table}`), (target:`{target_table}`) "
                            f"WHERE toString(source.`{from_col}`) = toString(target.`{to_col}`) "
                            f"MERGE (source)-[r:LINKED_TO {{from: '{from_col}', to: '{to_col}'}}]->(target)"
                        )
                        result = session.run(cypher_rel)
                        msg = result.consume()
                        stats["relationships_created"] += msg.counters.relationships_created

        logger.info(f"Data projection complete. Stats: {stats}")
        return {"status": "success", "stats": stats}

    except Exception as e:
        logger.error(f"Error projecting data to graph: {e}")
        return {"status": "error", "message": str(e)}

def get_primary_key(cursor, table_name):
    """Helper to find PK column name."""
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = cursor.fetchall()
    # cid, name, type, notnull, dflt_value, pk
    for col in cols:
        if col[5] == 1: # pk flag
            return col[1]
    return None
