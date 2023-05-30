import asyncio
from datetime import datetime
from typing import Annotated, List

import bittensor
import redis.asyncio as redis
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import rich

import btvep
from btvep.constants import COST, DEFAULT_UID
from btvep.db.api_keys import ApiKey
from btvep.db.api_keys import update as update_api_key
from btvep.db.utils import db, db_state_default, DB_PATH
from btvep.types import ChatResponse, Message
from btvep.validator_prompter import ValidatorPrompter

btvep.db.tables.create_all()
config = btvep.config.Config().load()
print("Starting http server with btvep config:")
rich.print_json(config.to_json())
print("Using SQLite database at", DB_PATH)
hotkey = bittensor.Keypair.create_from_mnemonic(config.hotkey_mnemonic)
validator_prompter = ValidatorPrompter(hotkey, DEFAULT_UID)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def reset_db_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        db.connect()
        yield
    finally:
        if not db.is_closed():
            db.close()


def missing_api_key():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API Key",
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_api_key(detail="Invalid API key"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def api_key_auth(input_api_key: str = Depends(oauth2_scheme)):
    if (input_api_key is None) or (input_api_key == ""):
        missing_api_key()

    api_key = ApiKey.get(ApiKey.api_key == input_api_key)
    if api_key is None:
        invalid_api_key("Invalid API key")
    elif api_key.enabled == 0:
        invalid_api_key("API key is disabled")
    elif (api_key.valid_until != -1) and (api_key.valid_until < datetime.now()):
        invalid_api_key(
            "API key has expired as of "
            + str(datetime.utcfromtimestamp(api_key.valid_until))
        )
    elif not api_key.has_unlimited_credits() and api_key.credits - COST < 0:
        invalid_api_key("Not enough credits")

    ###  API key is now validated. ###

    # Subtract cost if not unlimited
    credits = None if api_key.has_unlimited_credits() else api_key.credits - COST

    # Increment request count and potentially credits
    update_api_key(
        api_key.api_key,
        request_count=api_key.request_count + 1,
        credits=credits,
    )


app = FastAPI()


async def rate_limit_identifier(request: Request):
    return request.headers.get("Authorization").split(" ")[1]


@app.on_event("startup")
async def startup():
    if config.rate_limiting_enabled:
        try:
            redis_instance = redis.from_url(
                config.redis_url, encoding="utf-8", decode_responses=True
            )
            await FastAPILimiter.init(redis_instance, identifier=rate_limit_identifier)
        except redis.ConnectionError as e:
            rich.print(
                f"[red]ERROR:[/red] Could not connect to redis on [cyan]{config.redis_url}[/cyan]\n [red]Redis is required for rate limiting.[/red]"
            )
            raise e


def get_rate_limits():
    if not config.rate_limiting_enabled:
        return []

    return [
        Depends(RateLimiter(times=limit["times"], seconds=limit["seconds"]))
        for limit in config.global_rate_limits
    ]


@app.post(
    "/chat",
    dependencies=[
        Depends(get_db),
        Depends(api_key_auth),
        *get_rate_limits(),
    ],
)
def chat(
    authorization: Annotated[str | None, Header()] = None,
    uid: Annotated[int | None, Body()] = DEFAULT_UID,
    messages: Annotated[List[Message] | None, Body()] = None,
) -> ChatResponse:
    # An event loop for the thread is required by the bittensor library
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = validator_prompter.query_network(messages=messages, uid=uid)
    if response.is_success:
        btvep.db.request.Request.create(
            prompt=[message.json() for message in messages],
            response=response.completion,
            api_key=authorization.split(" ")[1],
            responder_hotkey=response.dest_hotkey,
        )
        return {
            "choices": [
                {
                    "index": 0,  # Hardcoded to 0 until support for multiple choices from bittensor
                    "message": {"role": "assistant", "content": response.completion},
                    "responder_hotkey": response.dest_hotkey,
                }
            ],
        }
    else:
        raise HTTPException(status_code=500, detail=response.return_message)
