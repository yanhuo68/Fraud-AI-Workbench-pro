# rag_sql/sql_validator.py

"""
SQL Query Validation and Sanitization

Prevents SQL injection by validating LLM-generated SQL queries before execution.
Only allows safe SELECT queries with proper constraints.
"""

import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Token
from sqlparse.tokens import Keyword, DML
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


# Dangerous SQL keywords that should never appear in queries
DANGEROUS_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE",
    "REPLACE", "MERGE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "PRAGMA", "ATTACH", "DETACH", "VACUUM"
}

# Dangerous SQL patterns (case-insensitive)
DANGEROUS_PATTERNS = [
    r";\s*DROP",  # SQL injection attempt
    r";\s*DELETE",
    r";\s*INSERT",
    r";\s*UPDATE",
    # r"--\s*",  # Comments are now stripped before validation
    r"/\*.*\*/",  # Block comments
    r"UNION\s+SELECT",  # Union-based injection
    r"INTO\s+OUTFILE",  # File operations
    r"LOAD_FILE",
    r"xp_cmdshell",  # Command execution (SQL Server)
]


class SQLValidationError(Exception):
    """Raised when SQL query fails validation."""
    pass


def validate_and_sanitize(
    sql: str,
    allowed_tables: Optional[List[str]] = None,
    max_rows: int = 10000
) -> Tuple[str, dict]:
    """
    Validate and sanitize an LLM-generated SQL query.
    
    Args:
        sql: SQL query string to validate
        allowed_tables: Optional list of allowed table names
        max_rows: Maximum number of rows to return (default: 10000)
    
    Returns:
        Tuple of (sanitized_sql, metadata_dict)
    
    Raises:
        SQLValidationError: If query is invalid or dangerous
    """
    # 1. Clean LLM extra formatting (Markdown only at first)
    # We want to check for dangerous patterns in the FULL text (minus ticks)
    if "```" in sql:
        blocks = re.findall(r"```(?:sql)?\s*(.*?)\s*```", sql, re.DOTALL | re.IGNORECASE)
        if blocks:
            sql = blocks[0]
        else:
            sql = sql.replace("```sql", "").replace("```", "")
    
    # 2. Check for dangerous patterns in the whole string
    # This prevents the truncation logic from hiding an injection
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            logger.warning(f"Dangerous pattern detected: {pattern}")
            raise SQLValidationError(f"Dangerous SQL pattern detected: {pattern}")
    
    # 2.1 BLOCK Multi-statement attempts (Raw Check)
    # If there are multiple statements before we even clean chatty text, we should be suspicious.
    # However, we only care if they are valid SQL statements.
    parsed_raw = sqlparse.parse(remove_comments(sql))
    if len(parsed_raw) > 1:
        # Check if the second statement looks like SQL (e.g. contains SELECT, INSERT, etc.)
        # If it's just "I hope this helps!", sqlparse might tag it as UNKNOWN but still 1 statement.
        # But if it's "SELECT * FROM x; DROP y", parsed_raw will have 2.
        significant_stmts = [s for s in parsed_raw if s.get_type() != 'UNKNOWN' or any(t.ttype in (Keyword, DML) for t in s.tokens)]
        if len(significant_stmts) > 1:
            raise SQLValidationError("Multiple SQL statements detected. Only one SELECT is allowed.")

    # 3. Comprehensive cleaning (Preamble, Trailing comments)
    sql = clean_llm_sql(sql)
    
    # Remove comments to avoid false positives in parsing
    sql_for_parsing = remove_comments(sql)
    
    # 4. Parse SQL (Cleaned version)
    try:
        parsed = sqlparse.parse(sql_for_parsing)
    except Exception as e:
        logger.error(f"SQL parsing failed: {e}")
        raise SQLValidationError(f"Invalid SQL syntax: {e}")
    
    if not parsed:
        raise SQLValidationError("Could not parse SQL query")
    
    statement = parsed[0]
    
    # 5. Check statement type - only SELECT allowed
    stmt_type = statement.get_type()
    if stmt_type != "SELECT":
        logger.warning(f"Non-SELECT query attempted: {stmt_type}")
        raise SQLValidationError(f"Only SELECT queries are allowed, got: {stmt_type}")
    
    # 6. Check for dangerous keywords
    sql_upper = sql.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in sql_upper:
            logger.warning(f"Dangerous keyword detected: {keyword}")
            raise SQLValidationError(f"Dangerous keyword not allowed: {keyword}")
    
    # 7. Extract table names and validate
    tables = extract_table_names(statement)
    if allowed_tables:
        if not tables:
             # If FROM was expected but not found, maybe invalid?
             # For SELECT 1; tables is empty.
             pass
        for table in tables:
            if table not in allowed_tables:
                logger.warning(f"Unauthorized table access: {table}")
                raise SQLValidationError(f"Table not allowed: {table}")
    
    # 8. Add LIMIT if missing
    sanitized_sql = add_limit_if_missing(sql, max_rows)
    
    # 9. FINAL sanitization (ensure no comments leak)
    sanitized_sql = remove_comments(sanitized_sql)
    
    metadata = {
        "original_sql": sql,
        "tables": tables,
        "has_limit": "LIMIT" in sql_upper,
        "added_limit": sanitized_sql != sql,
    }
    
    logger.info(f"SQL validation passed. Tables: {tables}")
    return sanitized_sql, metadata


def extract_table_names(statement) -> List[str]:
    """
    Extract table names from a parsed SQL statement.
    
    Args:
        statement: Parsed SQL statement from sqlparse
    
    Returns:
        List of table names
    """
    tables = []
    from_seen = False
    
    for token in statement.tokens:
        if from_seen:
            if token.is_whitespace or isinstance(token, sqlparse.sql.Comment):
                continue
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    tables.append(str(identifier.get_real_name()))
                from_seen = False
            elif isinstance(token, Identifier):
                tables.append(str(token.get_real_name()))
                from_seen = False
            else:
                # Some other token after FROM (like a subquery or another keyword)
                from_seen = False
        
        if token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
    
    return tables


def add_limit_if_missing(sql: str, max_rows: int) -> str:
    """
    Add LIMIT clause if missing from SQL query.
    
    Args:
        sql: SQL query string
        max_rows: Maximum number of rows
    
    Returns:
        SQL with LIMIT clause
    """
    sql_upper = sql.upper()
    
    # Check if LIMIT already exists
    if "LIMIT" in sql_upper:
        # Extract existing limit and ensure it's not too high
        limit_match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > max_rows:
                logger.info(f"Reducing LIMIT from {existing_limit} to {max_rows}")
                sql = re.sub(
                    r"LIMIT\s+\d+",
                    f"LIMIT {max_rows}",
                    sql,
                    flags=re.IGNORECASE
                )
        return sql
    
    # Add LIMIT clause
    # Handle queries with semicolon at the end
    sql = sql.rstrip(";").strip()
    sql = f"{sql} LIMIT {max_rows}"
    logger.info(f"Added LIMIT {max_rows} to query")
    
    return sql


def remove_comments(sql: str) -> str:
    """
    Remove SQL comments from query.
    
    Args:
        sql: SQL query string
    
    Returns:
        SQL without comments
    """
    # Remove single-line comments
    sql = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
    
    # Remove multi-line comments
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    
    return sql.strip()


def clean_llm_sql(sql: str) -> str:
    """
    Robustly clean SQL returned by an LLM.
    Handles:
    - Markdown code blocks (```sql ... ```)
    - Preamble text before the first SELECT/WITH
    - Trailing explanation after the last semicolon
    """
    # 1. Strip markdown code blocks if present
    if "```" in sql:
        # Try to find the content between first and last ```
        blocks = re.findall(r"```(?:sql)?\s*(.*?)\s*```", sql, re.DOTALL | re.IGNORECASE)
        if blocks:
            sql = blocks[0]
        else:
            # If not properly closed, just remove the ticks
            sql = sql.replace("```sql", "").replace("```", "")

    sql = sql.strip()

    # 2. Heuristic: Find the first SELECT, WITH, or PRAGMA (if allowed)
    # We want to discard any text like "Sure, here is your query: "
    match = re.search(r"\b(SELECT|WITH)\b", sql, re.IGNORECASE)
    if match:
        sql = sql[match.start():]

    # 3. Remove everything after the last semicolon if there is one
    # This discards trailing explanations like "This query joins tables X and Y..."
    if ";" in sql:
        sql = sql[:sql.rfind(";")+1]

    return sql.strip()


def validate_table_name(table_name: str) -> bool:
    """
    Validate that a table name is safe.
    
    Args:
        table_name: Table name to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Table name should only contain alphanumeric characters and underscores
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        return False
    
    # Check it's not a SQL keyword
    if table_name.upper() in DANGEROUS_KEYWORDS:
        return False
    
    return True


def validate_column_name(column_name: str) -> bool:
    """
    Validate that a column name is safe.
    
    Args:
        column_name: Column name to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Column name should only contain alphanumeric characters, underscores, and dots (for table.column)
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", column_name):
        return False
    
    return True
