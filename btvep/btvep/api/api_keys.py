from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel
from btvep.api.dependencies import authenticate_user

from btvep.db import api_keys
from btvep.db.user import User
from btvep.models.key import ApiKeyInDB

router = APIRouter()


class ApiKeyRequest(BaseModel):
    name: Optional[str] = "New API Key"
    default_query_strategy: Optional[str] = None


@router.post("/", status_code=201, response_model=ApiKeyInDB)
def create_api_key(
    request: ApiKeyRequest,
    user: User = Depends(authenticate_user),
):
    """
    Create a new API key.
    """
    api_key = api_keys.insert(name=request.name, user_id=user.id)
    return model_to_dict(api_key)


@router.get("/", response_model=List[ApiKeyInDB])
def list_api_keys(user: User = Depends(authenticate_user)):
    """
    List all API keys.
    """
    return api_keys.get_all_by_user_id(user.id)


@router.delete("/{query}")
def delete_api_key(query: str, user: User = Depends(authenticate_user)):
    """
    Deletes an API key.
    """
    count = api_keys.delete(query, user.id)
    if count == 0:
        raise HTTPException(status_code=404, detail=f"Key {query} not found")
    return {"detail": f"Deleted key {query}"}


@router.patch("/{query}")
def edit_api_key(
    query: str,
    request: ApiKeyRequest,
    user: User = Depends(authenticate_user),
):
    """
    Edit an API key.
    """
    fields_to_set_to_null = []
    if request.default_query_strategy is None:
        fields_to_set_to_null.append("default_query_strategy")

    api_keys.update(
        query=query,
        user_id=user.id,
        # Only allow name and default_query_strategy to be updated
        name=request.name,
        default_query_strategy=request.default_query_strategy,
        fields_to_nullify=fields_to_set_to_null,
    )
    updated_key = api_keys.get(query)
    if updated_key is None:
        raise HTTPException(status_code=404, detail=f"Key {query} not found")
    return updated_key
