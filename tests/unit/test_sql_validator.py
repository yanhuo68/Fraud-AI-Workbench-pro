import pytest
from rag_sql.sql_validator import (
    clean_llm_sql,
    remove_comments,
    extract_table_names,
    add_limit_if_missing,
    validate_table_name,
    validate_column_name,
    validate_and_sanitize,
    SQLValidationError
)

def test_clean_llm_sql():
    # Test markdown stripping
    sql_markdown = "```sql\nSELECT * FROM users;\n```"
    assert clean_llm_sql(sql_markdown) == "SELECT * FROM users;"
    
    # Test preamble removal
    sql_preamble = "Sure, here is your query: SELECT * FROM transactions"
    assert clean_llm_sql(sql_preamble) == "SELECT * FROM transactions"
    
    # Test trailing explanation removal
    sql_trailing = "SELECT * FROM data; This query retrieves all columns."
    assert clean_llm_sql(sql_trailing) == "SELECT * FROM data;"

def test_remove_comments():
    sql_comments = """
    -- Single line comment
    SELECT name /* inline comment */
    FROM users
    /* Multi-line
       comment */
    WHERE id = 1;
    """
    cleaned = remove_comments(sql_comments)
    assert "--" not in cleaned
    assert "/*" not in cleaned
    assert "SELECT name FROM users WHERE id = 1;" == " ".join(cleaned.split())

def test_add_limit_if_missing():
    # Case: Missing limit
    assert "LIMIT 100" in add_limit_if_missing("SELECT * FROM users", 100)
    
    # Case: Existing limit within bound
    assert "LIMIT 50" in add_limit_if_missing("SELECT * FROM users LIMIT 50", 100)
    
    # Case: Existing limit exceeds bound
    assert "LIMIT 100" in add_limit_if_missing("SELECT * FROM users LIMIT 500", 100)

def test_validate_identifiers():
    assert validate_table_name("users") is True
    assert validate_table_name("users_2023") is True
    assert validate_table_name("users; DROP TABLE users") is False
    assert validate_table_name("DROP") is False # Keyword check
    
    assert validate_column_name("user_id") is True
    assert validate_column_name("u.name") is True
    assert validate_column_name("name; --") is False

def test_validate_and_sanitize_security():
    # Test DANGEROUS_KEYWORDS
    # Note: DROP is caught by statement.get_type() != "SELECT" first
    with pytest.raises(SQLValidationError, match="Only SELECT queries are allowed, got: DROP"):
        validate_and_sanitize("DROP TABLE users")
    
    # Test DANGEROUS_PATTERNS
    with pytest.raises(SQLValidationError, match="Dangerous SQL pattern detected"):
        validate_and_sanitize("SELECT * FROM users; DELETE FROM transactions")
    
    with pytest.raises(SQLValidationError, match="Dangerous SQL pattern detected"):
        validate_and_sanitize("SELECT * FROM users UNION SELECT password FROM admins")

def test_multi_statement_blocking():
    # Test that multiple statements are blocked even if they are individually safe SELECTs
    with pytest.raises(SQLValidationError, match="Multiple SQL statements detected"):
        validate_and_sanitize("SELECT * FROM users; SELECT * FROM transactions")
    
    # Test that it allows a single trailing semicolon
    validate_and_sanitize("SELECT * FROM users;")

def test_validate_and_sanitize_success():
    sql = "SELECT name, age FROM users WHERE age > 18"
    sanitized, metadata = validate_and_sanitize(sql, allowed_tables=["users"], max_rows=50)
    
    assert "LIMIT 50" in sanitized
    assert "users" in metadata["tables"]
    assert metadata["added_limit"] is True

def test_unauthorized_table():
    with pytest.raises(SQLValidationError, match="Table not allowed: secret_table"):
        validate_and_sanitize("SELECT * FROM secret_table", allowed_tables=["users"])
