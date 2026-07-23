import os

import httpx
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Atlas Platform Gateway"
    VERSION: str = "1.0.0"

    # Public routes that don't require Gateway API Key validation
    PUBLIC_PREFIXES: tuple = ("docs", "redoc", "openapi.json", "api/v1/auth")

    @property
    def SERVICE_MAP(self) -> dict:
        return {
            "keysentry": os.getenv("KEYSENTRY_URL", "http://localhost:8001"),
        }

    def get_service_api_key(self, service_name: str) -> str | None:
        """
        Fetch the expected Atlas API key for a specific service.
        Expects environment variables like API_KEY_KEYSENTRY
        """
        return os.getenv(f"API_KEY_{service_name.upper()}")


settings = Settings()

# Shared HTTP client for connection pooling
http_client = httpx.AsyncClient()
