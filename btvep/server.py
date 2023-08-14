import asyncio
import json
import logging
from enum import Enum
from typing import Annotated, Dict, List

import bittensor
import rich
import uvicorn
from bittensor.utils.codes import code_to_string
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from btvep.chat_helpers import (
    process_responses,
    query_network,
    raise_for_all_failed_responses,
    setup_async_loop,
    ChatResponseException,
)
from btvep.db.api_keys import ApiKey
from btvep.db.api_keys import update as update_api_key
from btvep.db.user import User

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

from btvep.admin_api import (
    router as admin_router,
)  # composed router from the admin module
from btvep.btvep_models import (
    ChatResponse,
    Message,
)
from btvep.config import Config
from btvep.constants import COST, DEFAULT_NETUID, DEFAULT_UIDS
from btvep.db.request import Request
from btvep.db.tables import create_all as create_all_tables
from btvep.db.utils import DB_PATH
from btvep.fastapi_dependencies import (
    InitializeRateLimiting,
    VerifyAPIKeyAndLimit,
    authenticate_api_key,
    authenticate_user,
    get_db,
)
from btvep.metagraph import MetagraphSyncer
from btvep.validator_prompter import MetagraphNotSyncedException, ValidatorPrompter

create_all_tables()
config = Config().load().validate()

# Give info around configuration at server start
print("Config:")
rich.print_json(config.to_json(hide_mnemonic=True))
print("Using SQLite database at", DB_PATH)

# Initialize the validator prompter for bittensor
metagraph_syncer = MetagraphSyncer(DEFAULT_NETUID)
metagraph_syncer.start_sync_thread()
hotkey = bittensor.Keypair.create_from_mnemonic(config.hotkey_mnemonic)
validator_prompter = ValidatorPrompter(hotkey, metagraph_syncer)


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins. You can change this to allow specific domains.
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allows all methods. You can change this to allow specific HTTP methods.
    allow_headers=[
        "*"
    ],  # Allows all headers. You can change this to allow specific headers.
)

app.include_router(admin_router, prefix="/admin", tags=["Admin"])


@app.exception_handler(ChatResponseException)
async def unicorn_exception_handler(request: Request, exc: ChatResponseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "failed_responses": exc.failed_responses},
    )


@app.on_event("startup")
async def startup():
    if config.rate_limiting_enabled:
        await InitializeRateLimiting()


import json


# Endpoint Functions
@app.post("/conversation", dependencies=[Depends(get_db), Depends(authenticate_user)])
async def conversation(
    authorization: Annotated[str | None, Header()] = None,
    uids: Annotated[List[int] | None, Body()] = DEFAULT_UIDS,
    top_n: Annotated[
        int | None,
        Body(
            description="Query top miners based on incentive in the network. If set to for example 5, the top 5 miners will be sent the request. This parameter takes precidence over the uids parameter."
        ),
    ] = None,
    messages: Annotated[List[Message] | None, Body()] = None,
    user: ApiKey = Depends(authenticate_user),
) -> ChatResponse:
    setup_async_loop()
    prompter_responses = await query_network(validator_prompter, messages, uids, top_n)
    choices, failed_responses, all_failed = process_responses(
        prompter_responses, messages, authorization
    )

    # Increment user request counts (specific to conversation function)
    User.update(
        {
            "api_request_count": user.api_request_count + 1,
            "request_count": user.request_count + len(prompter_responses),
        }
    ).where(User.id == user.id).execute()

    if all_failed:
        raise_for_all_failed_responses(failed_responses)

    return {"choices": choices, "failed_responses": failed_responses}


@app.post(
    "/chat", dependencies=[Depends(get_db), Depends(lambda: VerifyAPIKeyAndLimit())]
)
async def chat(
    authorization: Annotated[str | None, Header()] = None,
    uids: Annotated[List[int] | None, Body()] = DEFAULT_UIDS,
    top_n: Annotated[
        int | None,
        Body(
            description="Query top miners based on incentive in the network. If set to for example 5, the top 5 miners will be sent the request. This parameter takes precidence over the uids parameter."
        ),
    ] = None,
    messages: Annotated[List[Message] | None, Body()] = None,
    api_key: ApiKey = Depends(authenticate_api_key),
) -> ChatResponse:
    setup_async_loop()
    prompter_responses = await query_network(validator_prompter, messages, uids, top_n)
    choices, failed_responses, all_failed = process_responses(
        prompter_responses, messages, authorization
    )

    # Subtract cost if not unlimited - Only pay for successful responses (specific to chat function)
    credits = (
        None
        if api_key.has_unlimited_credits() or all_failed
        else api_key.credits - COST * len(choices)
    )
    update_api_key(
        api_key.api_key,
        api_request_count=api_key.api_request_count + 1,
        request_count=api_key.request_count + len(prompter_responses),
        credits=credits,
    )

    if all_failed:
        raise_for_all_failed_responses(failed_responses)

    return {"choices": choices, "failed_responses": failed_responses}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
