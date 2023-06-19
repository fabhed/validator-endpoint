from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from btvep.db.request import Request

router = APIRouter()


class LogEntry(BaseModel):
    api_key: Optional[str]
    timestamp: int
    responder_hotkey: Optional[str]


class CountResponse(BaseModel):
    count: int


class CommonFilters(BaseModel):
    key: Optional[str] = None
    responder_hotkey: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None


class LogFilters(CommonFilters):
    lines: Optional[int] = 100


def apply_filters(query, filters: CommonFilters):
    if filters.key:
        query = query.where(Request.api_key_id == filters.key)
    if filters.start and filters.end:
        query = query.where(Request.timestamp.between(filters.start, filters.end))
    elif filters.start:
        query = query.where(Request.timestamp >= filters.start)
    elif filters.end:
        query = query.where(Request.timestamp <= filters.end)
    if filters.responder_hotkey:
        query = query.where(Request.responder_hotkey == filters.responder_hotkey)

    return query


@router.get("/", response_model=List[LogEntry])
async def get_logs(filters: LogFilters = Depends()):
    log_entries_query = Request.select().order_by(Request.timestamp.desc())

    log_entries_query = apply_filters(log_entries_query, filters)

    log_entries_query = log_entries_query.limit(filters.lines)

    log_entries = [LogEntry(**log) for log in log_entries_query.dicts().iterator()]
    return log_entries


@router.get("/count", response_model=CountResponse)
async def get_request_count(
    filters: CommonFilters = Depends(), unique_api_keys: Optional[bool] = False
):
    if unique_api_keys:
        count_query = Request.select(Request.api_key).distinct()
    else:
        count_query = Request.select()

    count_query = apply_filters(count_query, filters)

    return {"count": count_query.count()}
