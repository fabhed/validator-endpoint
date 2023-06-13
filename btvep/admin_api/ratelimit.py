import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from btvep.btvep_models import RateLimitEntry
from btvep.config import Config
from btvep.db import api_keys

router = APIRouter()


@router.get("/status")
async def get_rate_limit_status():
    config = Config().load()
    return {"rate_limiting_enabled": config.rate_limiting_enabled}


@router.post("/enable")
async def enable_rate_limiting():
    config = Config().load()
    config.rate_limiting_enabled = True
    config.save()
    return {"status": "Rate limiting enabled"}


@router.post("/disable")
async def disable_rate_limiting():
    config = Config().load()
    config.rate_limiting_enabled = False
    config.save()
    return {"status": "Rate limiting disabled"}


@router.get("/", response_model=List[RateLimitEntry])
async def get_rate_limits(api_key: Optional[str] = None):
    config = Config().load()
    if api_key:
        api_key = api_keys.get(api_key)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found.")
        if not api_key.rate_limits:
            return []
        return json.loads(api_key.rate_limits)
    else:
        return config.global_rate_limits


@router.post("/")
async def add_rate_limit(rate_limit: RateLimitEntry, api_key: Optional[str] = None):
    config = Config().load()
    if api_key:
        api_key = api_keys.get(api_key)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found.")
        if api_key.rate_limits is None:
            api_key.rate_limits = []
        else:
            api_key.rate_limits = json.loads(api_key.rate_limits)

        api_key.rate_limits.append(rate_limit.dict())
        api_key.rate_limits = json.dumps(api_key.rate_limits)
        api_key.save()
    else:
        config.global_rate_limits.append(rate_limit.dict())
        config.save()

    return {"status": "Rate limit added"}


@router.delete("/")
async def delete_rate_limit(index: int, api_key: Optional[str] = None):
    config = Config().load()
    if api_key:
        api_key = api_keys.get(api_key)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found.")

        if api_key.rate_limits is None:
            api_key.rate_limits = []
        else:
            api_key.rate_limits = json.loads(api_key.rate_limits)

        if index < 0 or index >= len(api_key.rate_limits):
            raise HTTPException(status_code=400, detail="Invalid index.")

        api_key.rate_limits.pop(index)
        api_key.rate_limits = json.dumps(api_key.rate_limits)
        api_key.save()
    else:
        if index < 0 or index >= len(config.global_rate_limits):
            raise HTTPException(status_code=400, detail="Invalid index.")
        config.global_rate_limits.pop(index)
        config.save()

    return {"status": "Rate limit deleted"}
