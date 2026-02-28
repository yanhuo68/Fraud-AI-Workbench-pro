# tests/unit/test_settings.py
"""
Unit tests for config/settings.py — Settings class validation,
env var overrides, helper methods, and validators.
"""
import pytest
import os
from unittest.mock import patch


def test_default_values():
    """Settings class should provide sane defaults for all fields."""
    from config.settings import Settings
    s = Settings(
        _env_file=None,  # ignore .env file
        openai_api_key="",
        secret_key="test-key",
    )
    assert s.api_host == "0.0.0.0"
    assert s.api_port == 8000
    assert s.max_file_size_mb == 100
    assert s.sql_timeout_seconds == 30
    assert s.sql_max_rows == 10000
    assert s.algorithm == "HS256"
    assert s.access_token_expire_minutes == 1440
    assert s.smtp_port == 587


def test_allowed_extensions_list():
    """get_allowed_extensions_list() should split comma-separated string correctly."""
    from config.settings import Settings
    s = Settings(_env_file=None, allowed_extensions="csv,pdf,txt,json")
    result = s.get_allowed_extensions_list()
    assert result == ["csv", "pdf", "txt", "json"]
    assert all(ext == ext.lower() for ext in result)


def test_max_file_size_bytes():
    """100 MB should convert to exactly 104857600 bytes."""
    from config.settings import Settings
    s = Settings(_env_file=None, max_file_size_mb=100)
    assert s.get_max_file_size_bytes() == 100 * 1024 * 1024


def test_allowed_origins_list():
    """get_allowed_origins_list() should split and strip each origin."""
    from config.settings import Settings
    s = Settings(
        _env_file=None,
        allowed_origins="http://localhost:8504, http://localhost:3000"
    )
    origins = s.get_allowed_origins_list()
    assert "http://localhost:8504" in origins
    assert "http://localhost:3000" in origins


def test_log_level_validator_valid():
    """Valid log levels should be accepted and uppercased."""
    from config.settings import Settings
    for level in ["debug", "INFO", "Warning", "ERROR", "critical"]:
        s = Settings(_env_file=None, log_level=level)
        assert s.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_log_level_validator_invalid():
    """Invalid log level should raise a ValueError."""
    from config.settings import Settings
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="VERBOSE")


def test_env_override_via_env_var(monkeypatch):
    """Environment variable should override .env file defaults."""
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "250")
    from config.settings import Settings
    s = Settings()
    assert s.max_file_size_mb == 250


def test_db_path_obj_returns_path():
    """db_path_obj property should return a Path object."""
    from config.settings import Settings
    from pathlib import Path
    s = Settings(_env_file=None)
    assert isinstance(s.db_path_obj, Path)


def test_uploads_dir_obj_returns_path():
    """uploads_dir_obj property should return a Path object."""
    from config.settings import Settings
    from pathlib import Path
    s = Settings(_env_file=None)
    assert isinstance(s.uploads_dir_obj, Path)


def test_api_key_defaults_empty():
    """All API key fields should default to empty string (not None)."""
    from config.settings import Settings
    s = Settings(_env_file=None, _secrets_dir=None)
    # API keys are optional — empty string means provider is disabled
    assert isinstance(s.openai_api_key, str)
    assert isinstance(s.anthropic_api_key, str)
    assert isinstance(s.google_api_key, str)
    assert isinstance(s.deepseek_api_key, str)
