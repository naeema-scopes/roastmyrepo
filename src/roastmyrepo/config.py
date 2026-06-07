"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    LLM_PROVIDER: str = "anthropic"  # "anthropic" or "openai"
    LLM_API_KEY: str = ""
    SERIOUS_MODE: bool = False
    OUTPUT_FORMAT: str = "text"  # "text" or "json"

    model_config = {"env_prefix": "ROAST_"}


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
