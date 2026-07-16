from fastapi import FastAPI
from gateway.core.config import settings, http_client
from gateway.api.api import api_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include API Router
app.include_router(api_router)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close HTTP client on application shutdown
    """
    await http_client.aclose()
