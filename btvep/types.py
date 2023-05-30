from typing import List, Literal
from pydantic import BaseModel


# RateLimit but with pydantic
class RateLimit(BaseModel):
    times: int
    seconds: int


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
