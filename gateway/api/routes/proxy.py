import httpx
from fastapi import APIRouter, Request, HTTPException, Response
from gateway.core.config import settings, http_client
from gateway.core.security import validate_api_key

router = APIRouter(tags=["Proxy"])

@router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def reverse_proxy(service_name: str, path: str, request: Request):
    """
    Dynamically routes incoming requests to the appropriate sidecar container.
    """
    base_url = settings.SERVICE_MAP.get(service_name)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found on Atlas.")
    
    # Construct the target URL (e.g., http://localhost:8001/api/v1/auth/login)
    target_url = f"{base_url}/{path}"
    
    # Validate API Key
    validate_api_key(request, service_name, path)

    # Forward the raw request to the sidecar
    try:
        req_body = await request.body()
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=req_body,
            params=request.query_params
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to communicate with sidecar '{service_name}': {exc}")
        
    content = response.content
    headers = dict(response.headers)
    
    # Rewrite OpenAPI JSON paths in the Swagger/ReDoc HTML so they fetch from the gateway's prefix
    if path.strip("/") in ("docs", "redoc"):
        content = content.replace(b'"/openapi.json"', f'"/{service_name}/openapi.json"'.encode())
        content = content.replace(b"'/openapi.json'", f"'/{service_name}/openapi.json'".encode())
        # Remove Content-Length so FastAPI recalculates it based on the new content length
        headers.pop("content-length", None)
        
    # Return the modified response from the sidecar
    return Response(
        content=content,
        status_code=response.status_code,
        headers=headers
    )
