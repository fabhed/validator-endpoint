import asyncio
from datetime import datetime
import time
from typing import Annotated, List, Literal

import bittensor
import redis.asyncio as redis
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Request, status

import btvep
from btvep.types import ChatResponse, Message
from btvep.validator_prompter import ValidatorPrompter

config = btvep.config.Config().load()
hotkey = bittensor.Keypair.create_from_mnemonic(config.hotkey_mnemonic)
validator_prompter = ValidatorPrompter(hotkey)

from fastapi.security import OAuth2PasswordBearer


from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

btvep.db.tables.create_all()


def missing_api_key():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API Key",
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_api_key(detail="Invalid API Key"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


cost = 1  # cost per request


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if (api_key is None) or (api_key == ""):
        missing_api_key()

    api_key = api_keys.get(api_key)
    if api_key is None:
        invalid_api_key("API Key is missing in header")
    elif api_key.enabled == 0:
        invalid_api_key("API Key is disabled")
    elif (api_key.valid_until != -1) and (api_key.valid_until < time.time()):
        invalid_api_key(
            "API Key has expired as of "
            + str(datetime.utcfromtimestamp(api_key.valid_until))
        )
    elif not api_key.has_unlimited_credits() and api_key.credits - cost < 0:
        invalid_api_key("Not enough credits")

    ###  API Key is now validated. ###

    # Subtract cost if not unlimited
    credits = None if api_key.has_unlimited_credits() else api_key.credits - cost
    # Increment request count and potentially credits
    api_keys.update(
        api_key.api_key,
        request_count=api_key.request_count + 1,
        credits=credits,
    )


app = FastAPI()


async def rate_limit_identifier(request: Request):
    return request.headers.get("Authorization").split(" ")[1]


@app.on_event("startup")
async def startup():
    redis_instance = redis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_instance, identifier=rate_limit_identifier)


from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


class ChatResponse(BaseModel):
    message: Message
    responder_hotkey: str


@app.post(
    "/chat",
    dependencies=[Depends(api_key_auth), Depends(RateLimiter(times=2, seconds=5))],
)
def chat(
    authorization: Annotated[str | None, Header()] = None,
    uid: Annotated[int | None, Body()] = 1,
    messages: Annotated[List[Message] | None, Body()] = None,
) -> ChatResponse:
    # An event loop for the thread is required by the bittensor library
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    response = validator_prompter.query_network(messages=messages, uid=uid)
    if response.is_success:
        btvep.db.request.Request.create(
            prompt=messages,
            response=response.completion,
            api_key=authorization.split(" ")[1],
        )
        return {
            "message": {"role": "assistant", "content": response.completion},
            "responder_hotkey": response.dest_hotkey,
        }
    else:
        raise HTTPException(status_code=500, detail=response.return_message)
