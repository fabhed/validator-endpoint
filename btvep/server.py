import asyncio
import json
from enum import Enum
from typing import Annotated, List

import bittensor
import rich
import uvicorn
from bittensor.utils.codes import code_to_string
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from btvep.admin_api import (
    router as admin_router,
)  # composed router from the admin module
from btvep.btvep_models import ChatResponse, Message
from btvep.config import Config
from btvep.constants import DEFAULT_NETUID, DEFAULT_UID
from btvep.db.request import Request
from btvep.db.tables import create_all as create_all_tables
from btvep.db.utils import DB_PATH
from btvep.fastapi_dependencies import InitializeRateLimiting, VerifyAndLimit, get_db
from btvep.validator_prompter import ValidatorPrompter

create_all_tables()
config = Config().load().validate()

# Give info around configuration at server start
print("Config:")
rich.print_json(config.to_json(hide_mnemonic=True))
print("Using SQLite database at", DB_PATH)

# Initialize the validator prompter for bittensor
hotkey = bittensor.Keypair.create_from_mnemonic(config.hotkey_mnemonic)
validator_prompter = ValidatorPrompter(hotkey, DEFAULT_NETUID)


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


@app.on_event("startup")
async def startup():
    if config.rate_limiting_enabled:
        await InitializeRateLimiting()


@app.post(
    "/chat",
    dependencies=[
        Depends(get_db),
        Depends(VerifyAndLimit()),
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

    return_code = None
    if isinstance(type(response.return_code), type(Enum)):
        return_code = response.return_code.value  # if return_code is an enum member
    else:
        return_code = response.return_code  # if return_code is not an enum member
    return_code_str = code_to_string(return_code)

    Request.create(
        is_api_success=True,
        prompt=json.dumps([message.dict() for message in messages]),
        api_key=authorization.split(" ")[1],
        response=response.completion,
        responder_hotkey=response.dest_hotkey,
        is_success=response.is_success,
        return_message=response.return_message,
        elapsed_time=response.elapsed,
        src_hotkey=response.src_hotkey,
        src_version=response.src_version,
        dest_version=response.dest_version,
        return_code=return_code_str,
    )
    if response.is_success:
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
