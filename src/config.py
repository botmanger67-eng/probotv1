"""Environment configuration loader for the Enterprise Telegram Bot.

Loads and validates configuration from environment variables and .env file.
Uses pydantic-settings for robust settings management.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, AnyHttpUrl


class Config(BaseSettings):
    """Application configuration loaded from environment variables.

    Attributes:
        APP_NAME: Name of the application.
        DEBUG: Enable debug mode.
        LOG_LEVEL: Logging level (e.g., DEBUG, INFO, WARNING).
        SECRET_KEY: Secret key for JWT and encryption.
        CSRF_SECRET: Secret key for CSRF protection.
        DATABASE_URL: PostgreSQL database connection URL.
        REDIS_URL: Redis connection URL.
        TELEGRAM_BOT_TOKEN: Telegram Bot API token.
        WEBHOOK_URL: Public URL for Telegram webhook.
        WEBHOOK_PATH: Path for Telegram webhook endpoint.
        WEBHOOK_PORT: Port for webhook server (default 8443).
        ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins.
        AI_ORCHESTRATOR_MODEL: Model name for AI orchestration.
        AI_ORCHESTRATOR_API_KEY: API key for AI service.
        AI_ORCHESTRATOR_ENDPOINT: Endpoint for AI service.
        CODE_GENERATION_TIMEOUT: Timeout in seconds for code generation.
        DEPLOYMENT_TIMEOUT: Timeout in seconds for deployment.
        RATE_LIMIT_DEFAULT: Default rate limit (requests per minute).
        RATE_LIMIT_AUTHENTICATED: Rate limit for authenticated users.
        RATE_LIMIT_PREMIUM: Rate limit for premium users.
        CACHE_TTL: Default cache TTL in seconds.
        SENTRY_DSN: Sentry DSN for error tracking (optional).
        ENVIRONMENT: Deployment environment (development, staging, production).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = Field(default="Enterprise Telegram Bot")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(...)
    CSRF_SECRET: str = Field(...)
    DATABASE_URL: PostgresDsn = Field(...)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    TELEGRAM_BOT_TOKEN: str = Field(...)
    WEBHOOK_URL: AnyHttpUrl = Field(...)
    WEBHOOK_PATH: str = Field(default="/webhook")
    WEBHOOK_PORT: int = Field(default=8443)
    ALLOWED_ORIGINS: str = Field(default="*")
    AI_ORCHESTRATOR_MODEL: str = Field(default="gpt-4")
    AI_ORCHESTRATOR_API_KEY: str = Field(...)
    AI_ORCHESTRATOR_ENDPOINT: AnyHttpUrl = Field(...)
    CODE_GENERATION_TIMEOUT: int = Field(default=30)
    DEPLOYMENT_TIMEOUT: int = Field(default=120)
    RATE_LIMIT_DEFAULT: int = Field(default=60)
    RATE_LIMIT_AUTHENTICATED: int = Field(default=120)
    RATE_LIMIT_PREMIUM: int = Field(default=300)
    CACHE_TTL: int = Field(default=300)
    SENTRY_DSN: Optional[str] = Field(default=None)
    ENVIRONMENT: str = Field(default="development")