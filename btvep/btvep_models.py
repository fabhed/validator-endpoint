from typing import List, Literal
from pydantic import BaseModel, Field


# RateLimit but with pydantic
class RateLimitEntry(BaseModel):
    times: int = Field(..., example=10)
    seconds: int = Field(..., example=60)


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


class ResponseMessage(BaseModel):
    """Message with an index and responder hotkey"""

    index: int
    responder_hotkey: str
    message: Message


class ChatResponse(BaseModel):
    choices: List[ResponseMessage]
