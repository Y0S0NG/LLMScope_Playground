"""Configuration management for Playground"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_title: str = "LLMScope Playground API"
    api_version: str = "1.0.0"

    # Database - supports both direct URL and components
    # For cloud deployment, use DATABASE_URL (Heroku, Railway, Render, etc.)
    # For local dev, use PLAYGROUND_DATABASE_URL
    database_url: str = os.getenv(
        "DATABASE_URL",  # Cloud platforms typically use this
        os.getenv(
            "PLAYGROUND_DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/llmscope_playground"
        )
    )

    # Redis (optional - not required for basic deployment)
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    redis_session_prefix: str = "llmscope:playground:session"
    redis_event_queue: str = "llmscope:playground:events"

    # Session Settings
    session_ttl_days: int = 7  # Sessions expire after 7 days of inactivity
    session_cleanup_interval_hours: int = 24  # Run cleanup job every 24 hours
    session_cookie_name: str = "llmscope_session_id"
    session_max_events_per_session: int = 10000  # Limit events per session

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    cors_origins: list = ["*"]  # Configure for production

    # AI Provider
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)

    # Rate Limiting (per session)
    rate_limit_requests_per_session: int = 100
    rate_limit_period_seconds: int = 60

    # Server settings
    port: int = int(os.getenv("PORT", "8001"))  # Cloud platforms set this
    host: str = os.getenv("HOST", "0.0.0.0")

    class Config:
        env_file = ".env"
        env_prefix = "PLAYGROUND_"
        extra = "allow"  # Allow extra fields from cloud platforms


settings = Settings()

# Fix postgres:// to postgresql:// for SQLAlchemy (Heroku uses postgres://)
if settings.database_url and settings.database_url.startswith("postgres://"):
    settings.database_url = settings.database_url.replace("postgres://", "postgresql://", 1)
