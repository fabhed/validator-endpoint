from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    name: Optional[str] = None
    valid_until: Optional[int] = -1
    credits: Optional[int] = -1
    enabled: Optional[bool] = True


class ApiKeyInDB(BaseModel):
    id: int
    api_key: str
    api_key_hint: str
    name: Optional[str] = None
    request_count: int
    valid_until: int
    credits: int
    enabled: bool
    rate_limits: Optional[str] = None
    rate_limits_enabled: bool = None
    created_at: int
    updated_at: int


class ApiKeyUpdate(BaseModel):
    api_key_hint: Optional[str] = None
    name: Optional[str] = None
    request_count: Optional[int] = None
    valid_until: Optional[int] = None
    credits: Optional[int] = None
    enabled: Optional[bool] = None
