import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "sample-data"

class Settings(BaseSettings):
    APP_NAME: str = "AgentForge"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "agentforge-super-secret-jwt-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM & Embedding Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./agentforge.db"
    DATABASE_URL_SYNC: str = "sqlite:///./agentforge.db"
    POSTGRES_DATABASE_URL: Optional[str] = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentforge"

    # Redis Configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # GitHub & External Integrations
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO: str = "25Rohit25/Agent-Forge"
    SLACK_WEBHOOK_URL: Optional[str] = None

    # Agent Limits
    MAX_AGENT_ITERATIONS: int = 10
    DEFAULT_TIMEOUT_SECONDS: int = 60

    # Paths
    SAMPLE_DATA_PATH: Path = SAMPLE_DATA_DIR
    SERVICES_DATA_FILE: Path = SAMPLE_DATA_DIR / "services" / "services.json"
    LOGS_DIR: Path = SAMPLE_DATA_DIR / "logs"
    KNOWLEDGE_BASE_DIR: Path = SAMPLE_DATA_DIR / "knowledge-base"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
