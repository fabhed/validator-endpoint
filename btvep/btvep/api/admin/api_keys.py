from datetime import datetime
from typing import List, Optional

import dateparser
from fastapi import APIRouter, Body, HTTPException
from playhouse.shortcuts import model_to_dict

from btvep.db import api_keys
from btvep.models.key import ApiKeyInDB
from btvep.btvep_models import RateLimitEntry

router = APIRouter()


@router.post("/", status_code=201, response_model=ApiKeyInDB)
def create_api_key(
    name: Optional[str] = Body(None),
    valid_until: Optional[int] = Body(-1),
    credits: Optional[int] = Body(-1),
    enabled: Optional[bool] = Body(True),
):
    """
    Create a new API key.
    """
    api_key = api_keys.insert(
        name=name, valid_until=valid_until, credits=credits, enabled=enabled
    )
    return model_to_dict(api_key)


@router.get("/", response_model=List[ApiKeyInDB])
def list_api_keys():
    """
    List all API keys.
    """
    return api_keys.get_all()


@router.delete("/{query}")
def delete_api_key(query: str):
    """
    Deletes an API key.
    """
    count = api_keys.delete(query)
    if count == 0:
        raise HTTPException(status_code=404, detail=f"Key {query} not found")
    return {"detail": f"Deleted key {query}"}


@router.patch("/{query}")
def edit_api_key(
    query: str,
    api_key_hint: Optional[str] = Body(None),
    name: Optional[str] = Body(None),
    request_count: Optional[int] = Body(None),
    valid_until: Optional[str] = Body(None),
    credits: Optional[int] = Body(None),
    enabled: Optional[bool] = Body(None),
    rate_limits: Optional[List[RateLimitEntry]] = Body(None),
    rate_limits_enabled: Optional[bool] = Body(None),
):
    """
    Edit an API key.
    """
    parsed_valid_until = None
    if valid_until is not None:
        if valid_until.lower() == "false" or valid_until.lower() == "-1":
            parsed_valid_until = -1
        else:
            parsed_valid_until = dateparser.parse(
                valid_until,
                settings={
                    "PREFER_DATES_FROM": "future",
                    "DATE_ORDER": "YMD",
                    "PREFER_DAY_OF_MONTH": "first",
                    "RELATIVE_BASE": datetime.now().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    ),
                },
            )

            if parsed_valid_until is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not parse date '{valid_until}'. Try another format.",
                )
            parsed_valid_until = int(parsed_valid_until.timestamp())
    api_keys.update(
        query=query,
        api_key_hint=api_key_hint,
        name=name,
        request_count=request_count,
        valid_until=parsed_valid_until,
        credits=credits,
        enabled=enabled,
        rate_limits=rate_limits,
        rate_limits_enabled=rate_limits_enabled,
    )
    updated_key = api_keys.get(query)
    if updated_key is None:
        raise HTTPException(status_code=404, detail=f"Key {query} not found")
    return updated_key
