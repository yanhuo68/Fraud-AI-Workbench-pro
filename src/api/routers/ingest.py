from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from typing import Any
from api.dependencies import get_current_user, requires_admin
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
from rag_sql.graph_utils import create_document_node
import logging
from pathlib import Path

from rag_sql.data_ingestion import ingest_uploaded_csv_dynamic
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file
    
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    allowed_extensions = settings.get_allowed_extensions_list()
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    logger.info(f"File validation passed: {file.filename} ({file_ext})")


@router.post("/file")
async def ingest_file(file: UploadFile = File(...), current_user: Any = Depends(get_current_user)):
    """
    Ingest a CSV file into the database.
    
    Args:
        file: Uploaded CSV file
    
    Returns:
        JSON with table name, row count, and columns
    """
    try:
        # Validate file
        validate_file_upload(file)
        
        # Read file content
        content = await file.read()
        max_size = settings.get_max_file_size_bytes()
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")
        
        # Save uploaded file to uploads directory
        try:
            uploads_path = settings.uploads_dir_obj / file.filename
            uploads_path.parent.mkdir(parents=True, exist_ok=True)
            uploads_path.write_bytes(content)
            logger.info(f"Uploaded file saved to {uploads_path}")
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")

        # Parse file based on extension
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        table_name = None
        
        # SQL Ingestion (CSVs only)
        if file_ext == "csv":
            try:
                # We still read into memory for SQL ingestion flow
                df = pd.read_csv(io.BytesIO(content))
                table_name, _, _ = ingest_uploaded_csv_dynamic(
                    df,
                    file.filename,
                    table_dataframes={},
                    table_pkfk={},
                    rebuild_kb=False  # we'll rebuild after docs handling
                )
                logger.info(f"Successfully ingested table: {table_name}")
            except Exception as e:
                # If SQL ingestion fails, we might still want to try graph? 
                # adhering to previous logic: throw error
                raise HTTPException(status_code=400, detail=f"Invalid CSV or SQL ingestion error: {e}")

        # Graph / Doc Ingestion (All supported types)
        # Use the saved file to extract text logic
        from rag_sql.file_loader import extract_text_from_file
        
        # Note: 'uploads_path' was defined and written in the try-block above (lines 66-72)
        # We must ensure it's accessible here. 
        # (Looking at original file, uploads_path variable might be local to try block scope if python strict? 
        # Python variables leak scope, but safety check: file was saved.)
        
        uploads_path = settings.uploads_dir_obj / file.filename
        if uploads_path.exists():
            text_content, _ = extract_text_from_file(uploads_path)
            
            if text_content:
                # 1. Save markdown doc (except for CSVs, usually distinct? 
                # Old logic: CSVs didn't save MD of content, only schema. 
                # New logic requested: "various kind in graph store".
                # If we convert CSV to text, we might as well save MD? 
                # Previous logic: CSV was handled separate for MD. 
                # Let's keep existing logic: Only non-CSV gets explicit MD file in docs/ 
                # (CSV gets schema MD from ingest_uploaded_csv_dynamic).
                # But for graph store, we send content.
                
                if file_ext != "csv":
                    docs_dir = settings.docs_dir_obj
                    docs_dir.mkdir(parents=True, exist_ok=True)
                    doc_path = docs_dir / f"{Path(file.filename).stem}.md"
                    doc_path.write_text(text_content, encoding="utf-8")
                    logger.info(f"Extracted text saved to {doc_path}")

                # Also store CSV content in graph store
                if file_ext == "csv":
                    csv_text = df.to_csv(index=False)
                    create_document_node(name=Path(file.filename).stem, content=csv_text, doc_type="csv")
                    
                    # Sync schema to graph (since table was created)
                    from rag_sql.graph_utils import sync_db_schema_to_graph
                    sync_db_schema_to_graph()
                    
                    # Rebuild vector store to ensure consistency if needed (though CSV schema is usually enough)
                    # For now, we rely on the schema markdown generated by ingest_uploaded_csv_dynamic for RAG
                
                # 2. Store in Graph (for non-CSV, this is the text_content; for CSV, it's already handled above)
                if file_ext != "csv":
                    create_document_node(name=Path(file.filename).stem, content=text_content, doc_type=file_ext)
                
                # 3. KB Rebuild 
                # (If CSV, schema MD is already there. If other, new MD is there.)
                from rag_sql.build_kb_index import build_vectorstore
                kb_dir = settings.kb_dir_obj
                docs_dir = settings.docs_dir_obj
                build_vectorstore(docs_dir=docs_dir, out_dir=kb_dir)
                logger.info("Knowledge base rebuilt")
                
                if not table_name:
                    table_name = Path(file.filename).stem

        return {
            "file_name": file.filename,
            "file_type": file_ext,
            "processed_as": "table_and_graph" if file_ext == "csv" else "graph_document",
            "table_name": table_name,
            "message": f"File '{file.filename}' processed successfully"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error executing raw sql ingest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-sql")
async def execute_sql_file(file: UploadFile = File(...), admin_user: Any = Depends(requires_admin)):
    """
    Execute an uploaded SQL script against the database.
    Also stores the script in the graph store as documentation.
    """
    try:
        if not file.filename.lower().endswith('.sql'):
            raise HTTPException(status_code=400, detail="Only .sql files are supported")
        
        content = await file.read()
        sql_script = content.decode('utf-8', errors='ignore')
        
        # 1. Execute against SQLite
        import sqlite3
        import re
        from config.settings import settings
        
        try:
            with sqlite3.connect(settings.db_path) as conn:
                # OPTIONAL: Parse script for CREATE TABLE statements and drop them first
                # Regex to find "CREATE TABLE [IF NOT EXISTS] table_name"
                # Matches: CREATE TABLE users, CREATE TABLE IF NOT EXISTS "my_table"
                # Case insensitive
                tables_to_drop = re.findall(
                    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"']?([a-zA-Z0-9_]+)[\"']?", 
                    sql_script, 
                    re.IGNORECASE
                )
                
                cursor = conn.cursor()
                if tables_to_drop:
                    logger.info(f"Found tables to potentially replace in script: {tables_to_drop}")
                    # Disable FK checks to allow dropping tables with dependencies temporarily
                    cursor.execute("PRAGMA foreign_keys = OFF;")
                    for table in tables_to_drop:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {table}")
                            logger.info(f"Dropped table '{table}' before recreating")
                        except Exception as drop_err:
                            logger.warning(f"Failed to drop table '{table}': {drop_err}")
                
                # Execute full script
                conn.executescript(sql_script)
                conn.commit()
                
            logger.info(f"Executed SQL script: {file.filename}")
        except Exception as e:
            logger.error(f"SQL execution failed for {file.filename}: {e}")
            raise HTTPException(status_code=400, detail=f"SQL Execution Error: {e}")
            
            # 2. Store in Graph Store (as Document)
        try:
            from rag_sql.graph_utils import create_document_node, sync_db_schema_to_graph
            
            # Store script doc
            create_document_node(
                name=Path(file.filename).stem, 
                content=sql_script, 
                doc_type="sql"
            )
            
            # Sync resulting schema changes to graph
            sync_db_schema_to_graph()
            
        except Exception as e:
            logger.error(f"Failed to store SQL doc in graph or sync schema: {e}")
            # Non-fatal
            
        return {
            "message": f"SQL script '{file.filename}' executed successfully",
            "stored_in_graph": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling SQL file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )