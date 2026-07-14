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
    
    # Validate JWT Token if service requires it (assuming all except auth require it for now)
    # Some paths might need to be public, but let's implement basic validation
    auth_header = request.headers.get("Authorization")
    
    # We allow /auth/ routes to pass through without JWT (for login/signup)
    if not path.startswith("auth/"):
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
        token = auth_header.split(" ")[1]
        jwt_secret = os.getenv("GOTRUE_JWT_SECRET")
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="GOTRUE_JWT_SECRET not configured on Gateway")
            
        try:
            import jwt
            # GoTrue uses HS256 by default
            jwt.decode(token, jwt_secret, algorithms=["HS256"], options={"verify_aud": False})
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

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
