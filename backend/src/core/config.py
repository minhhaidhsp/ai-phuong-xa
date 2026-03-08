# backend/src/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "AI Phuong Xa"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_SYNC_URL: str

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_LAW: str = "luat_phap_ly"

    # Ollama / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL_MAIN: str = "qwen2.5:7b"
    LLM_MODEL_FAST: str = "qwen2.5:1.5b"
    EMBED_MODEL: str = "nomic-embed-text"
    LLM_TIMEOUT_SECONDS: int = 60

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # LGSP
    LGSP_BASE_URL: str = "http://localhost:8000"
    LGSP_API_KEY: str = "dev-mock-key"
    LGSP_WARD_CODE: str = "79280001"


    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
settings = get_settings()
