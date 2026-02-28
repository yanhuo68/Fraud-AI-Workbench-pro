# tests/unit/test_rag_sql.py
"""
Unit tests for the SQL RAG pipeline.
Covers:
  - rag_sql.sql_utils.run_sql_query  — SQL execution helper
  - rag_sql.sql_validator            — clean + validate pipeline
  - rag_sql.langgraph_flow           — flow construction (import-level smoke)
"""
import pytest
import pandas as pd


class TestRunSQLQuery:
    """Tests for run_sql_query() in rag_sql/sql_utils.py."""

    def test_returns_dataframe_and_columns(self, tmp_path):
        """run_sql_query() should return (DataFrame, list[str]) for a valid SELECT."""
        import sqlite3
        db = tmp_path / "test.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE txn (id INTEGER, amount REAL)")
        con.execute("INSERT INTO txn VALUES (1, 99.5)")
        con.execute("INSERT INTO txn VALUES (2, 42.0)")
        con.commit()
        con.close()

        from rag_sql.sql_utils import run_sql_query
        df, cols = run_sql_query(
            "SELECT * FROM txn",
            db_path=str(db),
            validate=False  # skip SQL validator — we control the input
        )
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2
        assert set(cols) == {"id", "amount"}

    def test_returns_empty_df_for_no_rows(self, tmp_path):
        """Query returning zero rows should yield an empty DataFrame, not an error."""
        import sqlite3
        db = tmp_path / "empty.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE items (id INTEGER)")
        con.commit()
        con.close()

        from rag_sql.sql_utils import run_sql_query
        df, cols = run_sql_query(
            "SELECT * FROM items",
            db_path=str(db),
            validate=False
        )
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 0
        assert "id" in cols

    def test_raises_filenotfound_for_missing_db(self, tmp_path):
        """run_sql_query() must raise FileNotFoundError for a missing database path."""
        from rag_sql.sql_utils import run_sql_query
        with pytest.raises(FileNotFoundError):
            run_sql_query("SELECT 1", db_path=str(tmp_path / "nonexistent.db"))

    def test_columns_match_dataframe_columns(self, tmp_path):
        """The returned column list must match df.columns."""
        import sqlite3
        db = tmp_path / "cols.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE x (a INTEGER, b TEXT, c REAL)")
        con.execute("INSERT INTO x VALUES (1, 'hi', 3.14)")
        con.commit()
        con.close()

        from rag_sql.sql_utils import run_sql_query
        df, cols = run_sql_query("SELECT * FROM x", db_path=str(db), validate=False)
        assert list(df.columns) == cols


class TestSQLValidatorPipeline:
    """End-to-end tests: clean_llm_sql → validate_and_sanitize."""

    def test_clean_removes_markdown_fences(self):
        """clean_llm_sql() should strip markdown fences from LLM output."""
        from rag_sql.sql_validator import clean_llm_sql
        raw = "```sql\nSELECT 1;\n```"
        result = clean_llm_sql(raw)
        assert "```" not in result
        assert "SELECT" in result.upper()

    def test_clean_strips_natural_language_intro(self):
        """clean_llm_sql() should strip leading prose from the LLM."""
        from rag_sql.sql_validator import clean_llm_sql
        raw = "Sure! Here is the query:\nSELECT id FROM sales;"
        result = clean_llm_sql(raw)
        assert result.strip().upper().startswith("SELECT")

    def test_full_pipeline_clean_and_validate(self, tmp_path):
        """Cleaned LLM SQL should pass through validate_and_sanitize correctly."""
        import sqlite3
        db = tmp_path / "pipeline.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE sales (id INTEGER, amount REAL)")
        con.commit()
        con.close()

        from rag_sql.sql_validator import clean_llm_sql, validate_and_sanitize

        raw = "```sql\nSELECT id, amount FROM sales WHERE amount > 100;\n```"
        cleaned = clean_llm_sql(raw)
        sanitized, meta = validate_and_sanitize(
            cleaned,
            allowed_tables=["sales"],
            max_rows=100
        )
        assert "SELECT" in sanitized.upper()
        assert "LIMIT" in sanitized.upper()
        assert meta.get("tables") == ["sales"]

    def test_validate_blocks_non_select(self):
        """validate_and_sanitize() must reject non-SELECT statements."""
        from rag_sql.sql_validator import validate_and_sanitize, SQLValidationError
        with pytest.raises(SQLValidationError):
            validate_and_sanitize("DROP TABLE sales", allowed_tables=["sales"])

    def test_validate_blocks_disallowed_table(self):
        """validate_and_sanitize() must reject queries on disallowed tables."""
        from rag_sql.sql_validator import validate_and_sanitize, SQLValidationError
        with pytest.raises(SQLValidationError):
            validate_and_sanitize(
                "SELECT * FROM secret_table",
                allowed_tables=["sales"]
            )

    def test_validate_adds_limit(self):
        """validate_and_sanitize() should add a LIMIT clause if one is missing."""
        from rag_sql.sql_validator import validate_and_sanitize
        sql, _ = validate_and_sanitize(
            "SELECT * FROM sales",
            allowed_tables=["sales"],
            max_rows=50
        )
        assert "LIMIT" in sql.upper()


class TestLanggraphFlowImport:
    """Smoke-test that the langgraph flow module can be imported."""

    def test_import_langgraph_flow(self):
        """rag_sql.langgraph_flow must be importable without errors."""
        try:
            import rag_sql.langgraph_flow  # noqa: F401
        except ImportError as e:
            pytest.fail(f"rag_sql.langgraph_flow import failed: {e}")


class TestKnowledgeBaseImport:
    """Smoke-test that the knowledge base module can be imported."""

    def test_import_knowledge_base(self):
        """rag_sql.knowledge_base must be importable without errors."""
        try:
            import rag_sql.knowledge_base  # noqa: F401
        except ImportError as e:
            pytest.fail(f"rag_sql.knowledge_base import failed: {e}")
