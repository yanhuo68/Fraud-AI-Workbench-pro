# config/settings.py

"""
Centralized configuration management for Fraud Detection AI Workbench.


All configuration values should be accessed through this module to ensure
consistency across the application.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, AliasChoices


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # API Keys - read from system environment
    openai_api_key: str = Field(default="", validation_alias=AliasChoices("openai_api_key", "OPENAI_API_KEY"))
    deepseek_api_key: str = Field(default="", validation_alias=AliasChoices("deepseek_api_key", "DEEPSEEK_API_KEY"))
    google_api_key: str = Field(default="", validation_alias=AliasChoices("google_api_key", "GOOGLE_API_KEY"))
    anthropic_api_key: str = Field(default="", validation_alias=AliasChoices("anthropic_api_key", "ANTHROPIC_API_KEY"))
    
    # Database Configuration
    db_path: str = Field(default="data/db/rag.db", validation_alias=AliasChoices("db_path", "DB_PATH"))
    
    # API Configuration
    api_url: str = Field(default="http://localhost:8000", validation_alias=AliasChoices("api_url", "API_URL"))
    api_host: str = Field(default="0.0.0.0", validation_alias=AliasChoices("api_host", "API_HOST"))
    api_port: int = Field(default=8000, validation_alias=AliasChoices("api_port", "API_PORT"))
    
    # File Upload Configuration
    max_file_size_mb: int = Field(default=100, validation_alias=AliasChoices("max_file_size_mb", "MAX_FILE_SIZE_MB"))
    allowed_extensions: str = Field(
        default="csv,pdf,txt,json,md,png,jpg,jpeg,webp,mp3,wav,m4a,mp4,mov,avi",
        validation_alias=AliasChoices("allowed_extensions", "ALLOWED_EXTENSIONS")
    )
    uploads_dir: str = Field(default="Data/uploads", validation_alias=AliasChoices("uploads_dir", "UPLOADS_DIR"))
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:8504,http://localhost:3000",
        validation_alias=AliasChoices("allowed_origins", "ALLOWED_ORIGINS")
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("log_level", "LOG_LEVEL"))
    log_file: str = Field(default="logs/run.log", validation_alias=AliasChoices("log_file", "LOG_FILE"))
    
    # Model Configuration
    model_dir: str = Field(default="models/", validation_alias=AliasChoices("model_dir", "MODEL_DIR"))
    
    # Knowledge Base Configuration
    kb_dir: str = Field(default="data/kb", validation_alias=AliasChoices("kb_dir", "KB_DIR"))
    docs_dir: str = Field(default="docs", validation_alias=AliasChoices("docs_dir", "DOCS_DIR"))
    
    # Graph Store Configuration
    graph_store_uri: str = Field(default="bolt://localhost:7687", validation_alias=AliasChoices("graph_store_uri", "GRAPH_STORE_URI"))
    graph_store_user: str = Field(default="neo4j", validation_alias=AliasChoices("graph_store_user", "GRAPH_STORE_USER"))
    graph_store_password: str = Field(default="", validation_alias=AliasChoices("graph_store_password", "GRAPH_STORE_PASSWORD"))

    # SMTP Configuration (Optional)
    smtp_server: str = Field(default="", validation_alias=AliasChoices("smtp_server", "SMTP_SERVER"))
    smtp_port: int = Field(default=587, validation_alias=AliasChoices("smtp_port", "SMTP_PORT"))
    smtp_username: str = Field(default="", validation_alias=AliasChoices("smtp_username", "SMTP_USERNAME"))
    smtp_password: str = Field(default="", validation_alias=AliasChoices("smtp_password", "SMTP_PASSWORD"))
    smtp_sender_email: str = Field(default="", validation_alias=AliasChoices("smtp_sender_email", "SMTP_SENDER_EMAIL"))

    @property
    def graph_driver(self):
        """Return a Neo4j driver instance based on the configured URI and credentials."""
        from neo4j import GraphDatabase
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Connecting to Neo4j at {self.graph_store_uri} with user {self.graph_store_user}")
        
        if not self.graph_store_user or not self.graph_store_password:
             logger.warning("Neo4j credentials missing or incomplete!")
             
        return GraphDatabase.driver(self.graph_store_uri, auth=(self.graph_store_user, self.graph_store_password))

    
    # SQL Query Limits
    sql_timeout_seconds: int = Field(default=30, env="SQL_TIMEOUT_SECONDS")
    sql_max_rows: int = Field(default=10000, env="SQL_MAX_ROWS")
    
    # Security Configuration
    secret_key: str = Field(default="SUPER_SECRET_KEY_REPLACE_ME", validation_alias=AliasChoices("secret_key", "SECRET_KEY"))
    algorithm: str = Field(default="HS256", validation_alias=AliasChoices("algorithm", "ALGORITHM"))
    access_token_expire_minutes: int = Field(default=1440, validation_alias=AliasChoices("access_token_expire_minutes", "ACCESS_TOKEN_EXPIRE_MINUTES"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v
    
    @field_validator("db_path", "log_file", "model_dir", "kb_dir", "docs_dir", check_fields=False)
    @classmethod
    def ensure_parent_dirs(cls, v):
        """Ensure parent directories exist for file paths."""
        path = Path(v)
        if not path.is_absolute():
            # Make relative paths absolute from project root
            path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    def get_allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get list of allowed CORS origins."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def get_max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def db_path_obj(self) -> Path:
        """Get database path as Path object."""
        return Path(self.db_path)
    
    @property
    def log_file_obj(self) -> Path:
        """Get log file path as Path object."""
        return Path(self.log_file)
    
    @property
    def model_dir_obj(self) -> Path:
        """Get model directory as Path object."""
        return Path(self.model_dir)
    
    @property
    def kb_dir_obj(self) -> Path:
        """Get knowledge base directory as Path object."""
        return Path(self.kb_dir)
    
    @property
    def docs_dir_obj(self) -> Path:
        """Get docs directory as Path object."""
        return Path(self.docs_dir)

    @property
    def uploads_dir_obj(self) -> Path:
        """Get uploads directory as Path object."""
        return Path(self.uploads_dir)


# Global settings instance
settings = Settings()


# Convenience functions for backward compatibility
def get_db_path() -> Path:
    """Get database path."""
    return settings.db_path_obj


def get_api_url() -> str:
    """Get API URL."""
    return settings.api_url


def get_openai_api_key() -> str:
    """Get OpenAI API key."""
    return settings.openai_api_key


def get_deepseek_api_key() -> str:
    """Get DeepSeek API key."""
    return settings.deepseek_api_key
