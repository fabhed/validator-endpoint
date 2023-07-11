import asyncio
import json
import logging
import uuid
from enum import Enum
from typing import Annotated, Dict, List

import bittensor
import rich
import uvicorn
from bittensor.utils.codes import code_to_string
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from btvep.db.api_keys import ApiKey
from btvep.db.api_keys import update as update_api_key

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

from btvep.admin_api import (
    router as admin_router,
)  # composed router from the admin module
from btvep.btvep_models import (
    ChatResponse,
    ChatResponseChoice,
    FailedMinerResponse,
    Message,
)
from btvep.config import Config
from btvep.constants import COST, DEFAULT_NETUID, DEFAULT_UIDS
from btvep.db.request import Request
from btvep.db.tables import create_all as create_all_tables
from btvep.db.utils import DB_PATH
from btvep.fastapi_dependencies import (
    InitializeRateLimiting,
    VerifyAndLimit,
    authenticate_api_key,
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


class ChatResponseException(Exception):
    def __init__(self, detail: str, failed_responses: List[Dict], status_code: int):
        self.detail = detail
        self.failed_responses = failed_responses
        self.status_code = status_code


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


@app.post(
    "/chat",
    dependencies=[
        Depends(get_db),
        Depends(lambda: VerifyAndLimit(Depends(authenticate_api_key))),
    ],
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api_request_id = str(uuid.uuid4())
    prompter_responses = None
    try:
        prompter_responses = await validator_prompter.query_network(
            messages=messages, uids=uids, top_n=top_n
        )
    except MetagraphNotSyncedException as e:
        raise HTTPException(
            detail="Metagraph is not synced yet. Please try again later.",
            status_code=500,
        ) from e

    choices: List[ChatResponseChoice] = []
    failed_responses: List[FailedMinerResponse] = []
    all_failed = True

    success_index = 0
    failed_index = 0
    for p_response in prompter_responses:
        dendrite_res = p_response["dendrite_response"]
        uid = p_response["uid"]
        return_code = None
        if isinstance(type(dendrite_res.return_code), type(Enum)):
            return_code = (
                dendrite_res.return_code.value
            )  # if return_code is an enum member
        else:
            return_code = (
                dendrite_res.return_code
            )  # if return_code is not an enum member
        return_code_str = code_to_string(return_code)

        Request.create(
            is_api_success=True,
            api_request_id=api_request_id,
            prompt=json.dumps([message.dict() for message in messages]),
            api_key=authorization.split(" ")[1],
            response=dendrite_res.completion,
            responder_hotkey=dendrite_res.dest_hotkey,
            is_success=dendrite_res.is_success,
            return_message=dendrite_res.return_message,
            elapsed_time=dendrite_res.elapsed,
            src_version=dendrite_res.src_version,
            dest_version=dendrite_res.dest_version,
            return_code=return_code_str,
        )

        response_ms = int(dendrite_res.elapsed * 1000)

        if dendrite_res.is_success:
            choices.append(
                {
                    "index": success_index,
                    "message": {
                        "role": "assistant",
                        "content": dendrite_res.completion,
                    },
                    "uid": uid,
                    "responder_hotkey": dendrite_res.dest_hotkey,
                    "response_ms": response_ms,
                }
            )
            success_index += 1
            all_failed = False
        else:
            failed_responses.append(
                {
                    "index": failed_index,
                    "error": dendrite_res.return_message,
                    "uid": uid,
                    "responder_hotkey": dendrite_res.dest_hotkey,
                    "response_ms": response_ms,
                }
            )
            failed_index += 1

    if all_failed:
        raise ChatResponseException(
            status_code=502,  # Bad Gateway (we are the gateway to the network)
            detail="All miner responses have failed.",
            failed_responses=failed_responses,
        )

    # Subtract cost if not unlimited - Only pay for successful responses
    credits = (
        None
        if api_key.has_unlimited_credits()
        else api_key.credits - COST * len(choices)
    )

    # Increment request count and potentially credits
    update_api_key(
        api_key.api_key,
        api_request_count=api_key.api_request_count
        + 1,  # increment by one for each request to the API
        request_count=api_key.request_count
        + len(
            prompter_responses
        ),  # increment by the number of requests sent to the network
        credits=credits,
    )

    response_dict = {"choices": choices, "failed_responses": failed_responses}

    return response_dict


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
