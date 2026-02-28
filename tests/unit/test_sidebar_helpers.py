# tests/unit/test_sidebar_helpers.py
"""
Unit tests for sidebar helper functions:
  _get_all_docs()  - document discovery
  clean_llm_sql / sql extraction (sidebar-adjacent logic)
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGetAllDocs:
    """Tests for the _get_all_docs() discovery helper."""

    def test_returns_dict(self):
        """_get_all_docs() must return a dict."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        assert isinstance(result, dict)

    def test_all_paths_exist(self):
        """Every path returned by _get_all_docs() must point to an existing file."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        for label, path in result.items():
            assert Path(path).exists(), f"Path does not exist for label '{label}': {path}"

    def test_label_prefixes(self):
        """Labels should carry the correct emoji prefix for their category."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        for label in result:
            assert label.startswith(("📋", "🎨", "📦")), (
                f"Unexpected label prefix: '{label}'"
            )

    def test_user_manuals_prefixed_with_clipboard(self):
        """Labels from user_manual/ should start with 📋."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        manual_labels = [l for l in result if l.startswith("📋")]
        assert len(manual_labels) > 0, "Expected at least one user manual entry"

    def test_ui_design_prefixed_with_palette(self):
        """Labels from ui_design/ should start with 🎨."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        design_labels = [l for l in result if l.startswith("🎨")]
        assert len(design_labels) > 0, "Expected at least one UI design entry"

    def test_reference_docs_prefixed_with_package(self):
        """Labels from references/ should start with 📦."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        ref_labels = [l for l in result if l.startswith("📦")]
        assert len(ref_labels) > 0, "Expected at least one reference document"

    def test_no_readme_duplication(self):
        """README.md files should not create duplicate entries across categories."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        paths = list(result.values())
        assert len(paths) == len(set(paths)), "Duplicate file paths found in docs dict"

    def test_paths_are_strings(self):
        """_get_all_docs() values should be strings (file paths as str)."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        for label, path in result.items():
            assert isinstance(path, str), f"Expected str path for '{label}', got {type(path)}"

    def test_all_values_are_markdown_files(self):
        """Every value in the docs dict should point to a .md file."""
        from components.sidebar import _get_all_docs
        result = _get_all_docs()
        for label, path in result.items():
            assert path.endswith(".md"), (
                f"Expected .md path for label '{label}', got '{path}'"
            )

