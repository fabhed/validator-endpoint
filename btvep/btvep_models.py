from typing import List, Literal
from pydantic import BaseModel, Field


# RateLimit but with pydantic
class RateLimitEntry(BaseModel):
    times: int = Field(..., example=10)
    seconds: int = Field(..., example=60)


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


class ChatResponseChoice(BaseModel):
    """Message with an index and responder hotkey"""

    index: int
    uid: int
    responder_hotkey: str
    message: Message
    response_ms: int


class FailedMinerResponse(BaseModel):
    """Message with an index and responder hotkey"""

    index: int
    uid: int
    responder_hotkey: str
    error: str
    response_ms: int


class ChatResponse(BaseModel):
    choices: List[ChatResponseChoice]
    failed_responses: List[FailedMinerResponse]
