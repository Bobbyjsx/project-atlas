import httpx
from fastapi import FastAPI, Request, HTTPException, Response
import yaml
import os

app = FastAPI(title="Atlas Platform Gateway", version="1.0.0")

# Define the service map mapping route prefixes to internal sidecar ports
# These can be overridden via environment variables in production
SERVICE_MAP = {
    "keysentry": os.getenv("KEYSENTRY_URL", "http://localhost:8001"),
    "chess": os.getenv("CHESS_URL", "http://localhost:8002"),
}

# We use a single shared AsyncClient for HTTP connection pooling to maximize throughput
client = httpx.AsyncClient()

@app.get("/health")
async def health():
    """
    Health check endpoint for the Atlas Gateway.
    """
    return {"status": "healthy", "platform": "Project Atlas"}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def reverse_proxy(service_name: str, path: str, request: Request):
    """
    Dynamically routes incoming requests to the appropriate sidecar container.
    """
    base_url = SERVICE_MAP.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found on Atlas.")
    
    # Construct the target URL (e.g., http://localhost:8001/api/v1/auth/login)
    target_url = f"{base_url}/{path}"
    
    # Forward the raw request to the sidecar
    try:
        req_body = await request.body()
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=req_body,
            params=request.query_params
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to communicate with sidecar '{service_name}': {exc}")
    
    # Return the exact response from the sidecar
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()
