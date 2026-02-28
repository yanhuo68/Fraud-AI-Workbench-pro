# rag_sql/schema_consolidator.py

"""
Schema Consolidation Module

Consolidates individual table schemas into a central database_schema_reference.md file.
This provides a single source of truth for all database schemas.
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


def consolidate_schemas_to_reference(
    table_dataframes: Dict,
    table_pkfk: Dict,
    docs_dir: Path = None
) -> Path:
    """
    Consolidate all table schemas into database_schema_reference.md.
    
    Args:
        table_dataframes: Dictionary of table_name -> DataFrame
        table_pkfk: Dictionary of table_name -> {primary_key, foreign_keys}
        docs_dir: Documentation directory (default: from settings)
    
    Returns:
        Path to the consolidated schema reference file
    """
    if docs_dir is None:
        docs_dir = settings.docs_dir_obj
    
    docs_dir.mkdir(parents=True, exist_ok=True)
    reference_path = docs_dir / "database_schema_reference.md"
    
    logger.info(f"Consolidating {len(table_dataframes)} table schemas to {reference_path}")
    
    lines = []
    
    # Header
    lines.append("# Database Schema Reference\n\n")
    lines.append(f"_Last Updated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n\n")
    lines.append("This document provides exact schema definitions for all tables stored in the database. ")
    lines.append("LLMs must refer to these field names to avoid SQL hallucinations.\n\n")
    lines.append("---\n\n")
    
    # Table of Contents
    lines.append("## Table of Contents\n\n")
    for table_name in sorted(table_dataframes.keys()):
        lines.append(f"- [{table_name}](#{table_name})\n")
    lines.append("\n---\n\n")
    
    # Individual table schemas
    for table_name in sorted(table_dataframes.keys()):
        df = table_dataframes[table_name]
        pkfk_info = table_pkfk.get(table_name, {})
        pk = pkfk_info.get("primary_key")
        fks = pkfk_info.get("foreign_keys", [])
        
        # Table header
        lines.append(f"## {table_name}\n\n")
        
        # Primary Key
        lines.append("### Primary Key\n")
        if pk:
            lines.append(f"- `{pk}`\n\n")
        else:
            lines.append("- None detected\n\n")
        
        # Foreign Keys
        lines.append("### Foreign Keys\n")
        if fks:
            for fk in fks:
                table_A, colA, table_B, pkB = fk
                lines.append(f"- `{colA}` → `{table_B}.{pkB}`\n")
            lines.append("\n")
        else:
            lines.append("- None detected\n\n")
        
        # Columns table
        lines.append("### Columns\n\n")
        lines.append("| Column Name | Type | Nulls | Sample Value |\n")
        lines.append("|-------------|------|-------|-------------|\n")
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Map pandas dtype to SQL type
            if "int" in dtype:
                sql_type = "INTEGER"
            elif "float" in dtype:
                sql_type = "REAL"
            else:
                sql_type = "TEXT"
            
            nulls = df[col].isna().sum()
            sample = str(df[col].dropna().iloc[0]) if df[col].dropna().any() else ""
            
            # Truncate long samples
            if len(sample) > 50:
                sample = sample[:47] + "..."
            
            lines.append(f"| `{col}` | {sql_type} | {nulls} | {sample} |\n")
        
        lines.append("\n")
        
        # Metadata
        lines.append("### Metadata\n")
        lines.append(f"- **Total Rows**: {len(df):,}\n")
        lines.append(f"- **Total Columns**: {len(df.columns)}\n")
        lines.append(f"- **Memory Usage**: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB\n")
        lines.append("\n---\n\n")
    
    # Footer with key characteristics
    lines.append("## Key Schema Characteristics\n\n")
    lines.append("### General Notes\n")
    lines.append("- All schemas are auto-generated from uploaded CSV files\n")
    lines.append("- Primary keys are detected using heuristics (unique, non-null columns)\n")
    lines.append("- Foreign keys are detected by matching column names and value overlaps\n")
    lines.append("- NULL counts indicate data quality issues\n\n")
    
    lines.append("### Purpose of This Document\n")
    lines.append("LLMs rely on this schema reference to:\n")
    lines.append("- Avoid invalid SQL queries\n")
    lines.append("- Construct correct joins and filters\n")
    lines.append("- Reference applicable columns for analysis\n")
    lines.append("- Understand relationships between tables\n")
    
    # Write to file
    reference_path.write_text("".join(lines), encoding="utf-8")
    logger.info(f"Consolidated schema reference written to {reference_path}")
    
    return reference_path


def append_table_to_reference(
    table_name: str,
    df,
    primary_key: str,
    foreign_keys: List[tuple],
    docs_dir: Path = None
) -> Path:
    """
    Append or update a single table's schema in database_schema_reference.md.
    
    This is useful for incremental updates when a single table is uploaded.
    
    Args:
        table_name: Name of the table
        df: DataFrame with table data
        primary_key: Primary key column name
        foreign_keys: List of foreign key tuples
        docs_dir: Documentation directory (default: from settings)
    
    Returns:
        Path to the updated schema reference file
    """
    if docs_dir is None:
        docs_dir = settings.docs_dir_obj
    
    docs_dir.mkdir(parents=True, exist_ok=True)
    reference_path = docs_dir / "database_schema_reference.md"
    
    # For now, we'll use a simple approach: read existing content,
    # remove old section for this table if exists, and append new section
    
    # This is a simplified implementation
    # In production, you'd want to parse the markdown and update sections properly
    
    logger.info(f"Updating schema reference for table: {table_name}")
    
    # For the initial implementation, we'll just note that the table was added
    # A full implementation would parse and update the existing file
    
    return reference_path
