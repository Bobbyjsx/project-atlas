from fastapi import APIRouter
from gateway.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health():
    """
    Health check endpoint for the Atlas Gateway.
    """
    return {"status": "healthy", "platform": settings.PROJECT_NAME}
