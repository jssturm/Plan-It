"""Centralized configuration loaded from environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings sourced from environment variables."""

    # API authentication -- set TRAVEL_API_KEY in .env to protect endpoints
    API_KEY: str = os.getenv("TRAVEL_API_KEY", "")

    # Rate limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")

    # CORS origins (comma-separated)
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Search engine settings (self-contained, no API key needed)
    SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "12"))
    SEARCH_RATE_LIMIT_S: float = float(os.getenv("SEARCH_RATE_LIMIT_S", "1.2"))

    # Prompt sanitization: maximum input length to accept
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", "2000"))

    # Search backend selection — "ddg", "searxng", or "auto" (default: auto)
    # "auto" tries DuckDuckGo first, falls back to SearxNG on failure.
    SEARCH_BACKEND: str = os.getenv("SEARCH_BACKEND", "auto")

    # SearxNG public or self-hosted instance URL (used when backend is searxng or auto-failover)
    SEARXNG_INSTANCE: str = os.getenv("SEARXNG_INSTANCE", "https://searx.be")


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
