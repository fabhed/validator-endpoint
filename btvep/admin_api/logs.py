import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from btvep.btvep_models import Message
from btvep.db.request import Request

router = APIRouter()


class LogEntry(BaseModel):
    api_key: Optional[str]
    timestamp: int
    responder_hotkey: Optional[str]
    prompt: List[Message]

    # API fields - before request is sent to the bittensor network
    is_api_success: bool
    api_error: Optional[str]

    # Fields from DendriteCall class
    response: Optional[str]
    responder_hotkey: Optional[str]
    is_success: Optional[bool]
    return_message: Optional[str]
    elapsed_time: Optional[float]
    src_hotkey: Optional[str]
    src_version: Optional[int]
    dest_version: Optional[int]
    return_code: Optional[int]


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

    log_entries = []
    for log in log_entries_query.dicts().iterator():
        try:
            if log["prompt"] and log["prompt"].strip():
                prompt = json.loads(log["prompt"])
            else:
                prompt = []
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from log['prompt']: {log['prompt']}")
            print(f"Error: {e}")
            prompt = []

        # Update the 'prompt' in the log dict
        log["prompt"] = prompt

        log_entry = LogEntry(**log)
        log_entries.append(log_entry)

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
