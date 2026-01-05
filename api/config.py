"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str | None = os.environ.get("DATABASE_URL")
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20

    # AWS Textract
    AWS_ACCESS_KEY_ID: str | None = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.environ.get("AWS_SECRET_ACCES_KEY")
    AWS_REGION: str = "us-west-2"

    # Google Gemini
    GOOGLE_API_KEY: str | None = os.environ.get("GOOGLE_API_KEY")
    GEMINI_MODEL: str = "gemini-3.0-flash-exp"

    # Storage
    STORAGE_PATH: str = "/app/storage/receipts"

    # Processing
    TEXTRACT_MAX_RETRIES: int = 3
    GEMINI_MAX_RETRIES: int = 3
    VALIDATION_TOLERANCE: float = 0.02  # 2% tolerance for sum validation

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
