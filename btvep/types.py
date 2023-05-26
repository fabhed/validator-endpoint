from typing import Literal
from pydantic import BaseModel


# RateLimit but with pydantic
class RateLimit(BaseModel):
    times: int
    seconds: int


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


class ChatResponse(BaseModel):
    message: Message
    responder_hotkey: str
