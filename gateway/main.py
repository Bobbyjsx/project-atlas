import logging
from fastapi import FastAPI
from gateway.core.config import settings, http_client
from gateway.api.api import api_router

# Configure logger
logger = logging.getLogger("atlas.gateway")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include API Router
app.include_router(api_router)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close HTTP client on application shutdown
    """
    await http_client.aclose()
