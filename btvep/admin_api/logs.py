from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from btvep.db.request import Request

router = APIRouter()


class LogEntry(BaseModel):
    api_key_id: Optional[str]
    timestamp: datetime
    responder_hotkey: Optional[str]
    # Add other fields of the Log Entry here


class LogFilters(BaseModel):
    key: Optional[str] = None
    responder_hotkey: Optional[str] = None
    lines: Optional[int] = 100
    start: Optional[datetime] = None
    end: Optional[datetime] = None


@router.get("/", response_model=List[LogEntry])
async def get_logs(filters: LogFilters = Depends()):
    log_entries_query = (
        Request.select().order_by(Request.timestamp.desc()).limit(filters.lines)
    )

    if filters.key:
        log_entries_query = log_entries_query.where(Request.api_key_id == filters.key)
    if filters.start and filters.end:
        log_entries_query = log_entries_query.where(
            Request.timestamp.between(filters.start, filters.end)
        )
    elif filters.start:
        log_entries_query = log_entries_query.where(Request.timestamp >= filters.start)
    elif filters.end:
        log_entries_query = log_entries_query.where(Request.timestamp <= filters.end)
    if filters.responder_hotkey:
        log_entries_query = log_entries_query.where(
            Request.responder_hotkey == filters.responder_hotkey
        )

    log_entries = [LogEntry(**log) for log in log_entries_query.dicts().iterator()]
    return log_entries
