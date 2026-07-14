from fastapi import APIRouter
from gateway.api.routes import health, proxy

api_router = APIRouter()

# Register routes
api_router.include_router(health.router)
api_router.include_router(proxy.router)
