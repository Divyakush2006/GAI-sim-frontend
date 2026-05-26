"""
GovernAI Studio — Configuration
All environment variables with free-tier defaults.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === App ===
    APP_NAME: str = "GovernAI Studio"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # === Database (Neon Free Tier) ===
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@host/governai"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 2

    # === LLM Providers (All Free Tiers) ===
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""  # Comma-separated keys for rotation
    GROQ_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    SAMBANOVA_API_KEY: str = ""

    # Primary provider for each AI role
    LLM_ROLE_DIRECTOR: str = "gemini"
    LLM_ROLE_NPC: str = "groq"          # Fast streaming for chat
    LLM_ROLE_WHISPERER: str = "gemini"   # Best reasoning
    LLM_ROLE_DRAFTING: str = "cerebras"  # High throughput
    LLM_ROLE_COACH: str = "gemini"       # Best nuance

    # === Auth ===
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAGIC_LINK_EXPIRE_MINUTES: int = 15

    # === Email (Resend Free: 100/day) ===
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "auth@governai.studio"
    ALLOWED_EMAIL_DOMAINS: list[str] = ["gov.in", "nic.in", "governai.in"]

    # === GraphRAG (LightRAG) ===
    GRAPH_DATA_DIR: str = "./graph_data"
    CORPUS_RAW_DIR: str = "./corpus/raw"
    CORPUS_PROCESSED_DIR: str = "./corpus/processed"
    EMBEDDING_DIM: int = 3072
    CHUNK_TOKEN_SIZE: int = 300
    CHUNK_OVERLAP: int = 50

    # === Rate Limiting ===
    GEMINI_RPM: int = 15
    GROQ_RPM: int = 30
    CEREBRAS_RPM: int = 30
    SAMBANOVA_RPM: int = 20

    # === CORS ===
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://governai.vercel.app",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
