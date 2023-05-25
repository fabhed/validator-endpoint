import typing
from pydantic import BaseModel


# RateLimit but with pydantic
class RateLimit(BaseModel):
    times: int
    seconds: int
