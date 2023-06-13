from fastapi import APIRouter

from .key import router as api_key_router

# Compose all routers into a single router
router = APIRouter()
router.include_router(api_key_router, prefix="/api-keys")
# router.include_router(configs_router, prefix="/configs")
# router.include_router(rate_limits_router, prefix="/rate-limits")
# router.include_router(logs_router, prefix="/logs")
