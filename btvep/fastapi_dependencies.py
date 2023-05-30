from datetime import datetime
import json
from typing import Annotated

import redis.asyncio
import rich
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from btvep.config import Config
from btvep.constants import COST
from btvep.db.api_keys import ApiKey
from btvep.db.api_keys import get_by_key as get_api_key_by_key
from btvep.db.api_keys import update as update_api_key
from btvep.db.utils import db, db_state_default

config = Config().load()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


from starlette.requests import Request
from starlette.responses import Response


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


async def InitializeRateLimiting():
    try:
        redis_instance = redis.asyncio.from_url(
            config.redis_url, encoding="utf-8", decode_responses=True
        )

        async def rate_limit_identifier(request: Request):
            return request.headers.get("Authorization").split(" ")[1]

        await FastAPILimiter.init(redis_instance, identifier=rate_limit_identifier)
    except redis.asyncio.ConnectionError as e:
        rich.print(
            f"[red]ERROR:[/red] Could not connect to redis on [cyan]{config.redis_url}[/cyan]\n [red]Redis is required for rate limiting.[/red]"
        )
        raise e


def authenticate_api_key(input_api_key: str = Depends(oauth2_scheme)) -> ApiKey:
    def raiseKeyError(detail: str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if (input_api_key is None) or (input_api_key == ""):
        raiseKeyError("Missing API key")

    api_key = get_api_key_by_key(input_api_key)
    if api_key is None:
        raiseKeyError("Invalid API key")
    elif api_key.enabled == 0:
        raiseKeyError("API key is disabled")
    elif (api_key.valid_until != -1) and (api_key.valid_until < datetime.now()):
        raiseKeyError(
            "API key has expired as of "
            + str(datetime.utcfromtimestamp(api_key.valid_until))
        )
    elif not api_key.has_unlimited_credits() and api_key.credits - COST < 0:
        raiseKeyError("Not enough credits")

    ###  API key is now validated. ###

    # Subtract cost if not unlimited
    credits = None if api_key.has_unlimited_credits() else api_key.credits - COST

    # Increment request count and potentially credits
    update_api_key(
        api_key.api_key,
        request_count=api_key.request_count + 1,
        credits=credits,
    )

    return api_key


def get_rate_limits(api_key: str = None) -> list[RateLimiter]:
    """Get rate limits. Leave api_key as None to get global rate limits."""

    if not config.rate_limiting_enabled:
        return []

    print("api_key", api_key)
    rate_limits = None
    if api_key is not None:
        rate_limits = json.loads(api_key.rate_limits)
    elif config.rate_limiting_enabled:
        rate_limits = config.global_rate_limits

    return [
        RateLimiter(times=limit["times"], seconds=limit["seconds"])
        for limit in rate_limits
    ]


global_rate_limits = get_rate_limits()


def VerifyAndLimit():
    async def a(
        request: Request,
        response: Response,
        api_key: Annotated[ApiKey, Depends(authenticate_api_key)],
    ):
        for ratelimit in (
            get_rate_limits(api_key)
            if api_key and api_key.rate_limits
            else global_rate_limits
        ):
            await ratelimit(request, response)

    return a
