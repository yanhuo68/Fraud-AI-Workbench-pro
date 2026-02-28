import logging
from config.settings import settings

logger = logging.getLogger(__name__)

def create_document_node(name: str, content: str, doc_type: str) -> None:
    """Create or update a Document node in the configured Neo4j graph store.

    Args:
        name: Identifier for the document (typically the file stem).
        content: Full textual content extracted from the file.
        doc_type: File extension/type (e.g., "pdf", "txt", "md", "json").
    """
    try:
        driver = settings.graph_driver
        with driver.session() as session:
            session.run(
                "MERGE (d:Document {name: $name}) "
                "SET d.content = $content, d.type = $type",
                name=name,
                content=content,
                type=doc_type,
            )
        logger.info(f"Document node '{name}' of type '{doc_type}' stored in graph store")
    except Exception as e:
        logger.error(f"Failed to store document node '{name}' in graph store (non‑fatal): {e}")
        # Continue without raising to avoid breaking ingestion when graph store is unavailable

def sync_db_schema_to_graph(db_path: str = None) -> None:
    """
    Introspect the SQLite database and sync table nodes and relationships 
    (Foreign Keys) to the Neo4j graph store.
    """
    try:
        import sqlite3
        from pathlib import Path
        
        if db_path is None:
            db_path = settings.db_path
            
        if not Path(db_path).exists():
            logger.warning(f"Database file not found at {db_path}, skipping schema sync")
            return

        driver = settings.graph_driver
        
        # 1. Get Tables and Foreign Keys from SQLite
        tables = []
        relationships = []
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            table_rows = cursor.fetchall()
            
            for row in table_rows:
                table_name = row[0]
                tables.append(table_name)
                
                # Get Foreign Keys for this table
                # PRAGMA foreign_key_list(table-name) returns:
                # id, seq, table, from, to, on_update, on_delete, match
                try:
                    cursor_fk = conn.cursor()
                    cursor_fk.execute(f"PRAGMA foreign_key_list('{table_name}')")
                    fks = cursor_fk.fetchall()
                    for fk in fks:
                        target_table = fk[2]
                        from_col = fk[3]
                        to_col = fk[4]
                        
                        # Add relationship tuple: (source_table, target_table, type, properties)
                        relationships.append({
                            "source": table_name,
                            "target": target_table,
                            "type": "REFERENCES",
                            "props": {"from_col": from_col, "to_col": to_col}
                        })
                except Exception as e:
                    logger.warning(f"Error reading FKs for table {table_name}: {e}")

        # 2. Update Neo4j
        with driver.session() as session:
            # Create Table Nodes
            for table in tables:
                logger.info(f"Syncing Table Node: {table}")
                session.run(
                    "MERGE (t:Table {name: $name})",
                    name=table
                )
            
            # Create Relationships
            for rel in relationships:
                logger.info(f"Syncing Relationship: {rel['source']} -> {rel['target']} (props: {rel['props']})")
                # Merge relationship based on table names
                # Using MERGE on relationship ensures no duplicates
                # CRITICAL FIX: MERGE the target node too, in case casing differs or it wasn't scanned
                session.run(
                    """
                    MERGE (s:Table {name: $source})
                    MERGE (t:Table {name: $target})
                    MERGE (s)-[r:REFERENCES]->(t)
                    SET r.from_col = $from_col, r.to_col = $to_col
                    """,
                    source=rel["source"],
                    target=rel["target"],
                    from_col=rel["props"]["from_col"],
                    to_col=rel["props"]["to_col"]
                )
        
        logger.info(f"Synced schema to graph: {len(tables)} tables, {len(relationships)} relationships")
        
    except Exception as e:
        logger.error(f"Failed to sync database schema to graph: {e}")
