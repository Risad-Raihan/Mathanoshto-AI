"""
Centralized configuration management using Pydantic
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    tavily_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./chat_history.db"
    
    # Application
    app_name: str = "Mathanoshto AI"
    debug_mode: bool = False
    
    # File Storage
    upload_dir: Path = Path("uploads")
    max_upload_size_mb: int = 10
    
    # Model Configuration
    model_config_path: Path = Path("backend/config/models.yaml")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Global settings instance
settings = Settings()

