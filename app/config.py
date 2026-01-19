import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl, ValidationError


load_dotenv()


class Settings(BaseModel):
    app_name: str = "Neuram PDF Summarizer"
    openrouter_api_key: Optional[str] = Field(default=None, description="API key for OpenRouter")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", description="Model ID for OpenRouter")
    openrouter_base_url: HttpUrl = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API",
    )
    tavily_api_key: Optional[str] = Field(default=None, description="API key for Tavily search")
    tavily_base_url: HttpUrl = Field(
        default="https://api.tavily.com/search",
        description="Base URL for Tavily API",
    )
    request_timeout_seconds: float = Field(default=30.0, description="Timeout for outbound HTTP requests")

    class Config:
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528:free"),
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        )
    except ValidationError as exc:
        raise RuntimeError(f"Invalid environment configuration: {exc}") from exc

