"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.1
    
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS: int = 4000
    ANTHROPIC_TEMPERATURE: float = 0.1
    
    # Database
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///./rhinoai.db"
    
    # Backend
    BACKEND_PORT: int = 8000
    UPLOAD_DIR: str = "/tmp/rhino_uploads"
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
