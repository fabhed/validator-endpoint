from fastapi import APIRouter, Depends

from btvep.api.dependencies import VerifyAPIKeyAndLimit, authenticate_user, get_db
from btvep.api.admin import (
    router as admin_router,
)
from .api_keys import router as key_router
from .conversation import router as conversation_router
from .chat import router as chat_router

# Compose routers into a single router


all_endpoints = APIRouter()

all_endpoints.include_router(admin_router, prefix="/admin", tags=["Admin"])

all_endpoints.include_router(
    key_router,
    prefix="/api-keys",
    dependencies=[Depends(get_db), Depends(authenticate_user)],
)

all_endpoints.include_router(
    conversation_router, dependencies=[Depends(get_db), Depends(authenticate_user)]
)
all_endpoints.include_router(
    chat_router, dependencies=[Depends(get_db), Depends(lambda: VerifyAPIKeyAndLimit())]
)
