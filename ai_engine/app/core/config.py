import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file automatically
load_dotenv()


class Settings(BaseModel):
    """Global configuration settings for the AI Engine."""
    provider_type: str = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"),
        description="LLM provider type: 'mock', 'openai'"
    )
    api_key: str = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
        description="API Key for LLM provider"
    )
    model_name: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"),
        description="Default model identifier"
    )
    base_url: str = Field(
        default_factory=lambda: os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        description="Base URL for LLM provider API"
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "30.0")),
        description="API request timeout in seconds"
    )


settings = Settings()
