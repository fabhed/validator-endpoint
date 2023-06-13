from fastapi import APIRouter

from .key import router as key_router
from .logs import router as logs_router
from .config import router as config_router
from .ratelimit import router as ratelimit_router

# Compose all routers into a single router
router = APIRouter()
router.include_router(key_router, prefix="/api-keys")
router.include_router(config_router, prefix="/config")
router.include_router(logs_router, prefix="/logs")
router.include_router(ratelimit_router, prefix="/rate-limits")
