import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from gateway.core.config import http_client, settings
from gateway.core.security import validate_api_key

router = APIRouter(tags=["Proxy"])


async def _stream_response(
    method: str,
    url: str,
    headers: dict,
    content: bytes,
    params,
):
    """Pass SSE chunks from the sidecar straight to the client without buffering."""
    async with http_client.stream(
        method, url, headers=headers, content=content, params=params
    ) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@router.api_route(
    "/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def reverse_proxy(service_name: str, path: str, request: Request):
    """
    Dynamically routes incoming requests to the appropriate sidecar container.
    """
    base_url = settings.SERVICE_MAP.get(service_name)
    if not base_url:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found on Atlas."
        )

    # Construct the target URL (e.g., http://localhost:8001/api/v1/auth/login)
    target_url = f"{base_url}/{path}"

    # Validate API Key
    validate_api_key(request, service_name, path)

    req_body = await request.body()
    headers = dict(request.headers)

    # SSE path — stream chunks straight through without buffering
    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            _stream_response(request.method, target_url, headers, req_body, request.query_params),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Forward the raw request to the sidecar (buffered path)
    try:
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=req_body,
            params=request.query_params,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with sidecar '{service_name}': {exc}",
        )

    content = response.content
    resp_headers = dict(response.headers)

    if response.status_code >= 400:
        from gateway.core.logger import logger

        logger.error(
            f"Proxy error {response.status_code} from {service_name}/{path} - Request Body: {req_body} - Response Body: {content}"
        )

    # Rewrite OpenAPI JSON paths in the Swagger/ReDoc HTML so they fetch from the gateway's prefix
    if path.strip("/") in ("docs", "redoc"):
        content = content.replace(
            b'"/openapi.json"', f'"/{service_name}/openapi.json"'.encode()
        )
        content = content.replace(
            b"'/openapi.json'", f"'/{service_name}/openapi.json'".encode()
        )
        # Remove Content-Length so FastAPI recalculates it based on the new content length
        resp_headers.pop("content-length", None)

    # Return the modified response from the sidecar
    return Response(content=content, status_code=response.status_code, headers=resp_headers)

