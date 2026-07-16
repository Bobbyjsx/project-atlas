from fastapi import Request, HTTPException
from gateway.core.config import settings


def validate_api_key(request: Request, service_name: str, path: str):
    """
    Validates the X-Atlas-Api-Key header.
    Allows public routes defined in settings.PUBLIC_PREFIXES to pass through.
    """
    # Check if path contains or starts with any of the public prefixes (like docs, redoc)
    for prefix in settings.PUBLIC_PREFIXES:
        if path.startswith(prefix) or f"/{prefix}" in path:
            return

    provided_key = request.headers.get("x-atlas-api-key")
    if not provided_key:
        raise HTTPException(status_code=401, detail="Missing X-Atlas-Api-Key header")

    expected_key = settings.get_service_api_key(service_name)
    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail=f"No API key configured for service '{service_name}' on the Gateway.",
        )

    if provided_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API Key for this service")
