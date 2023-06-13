import asyncio
from typing import Annotated, List

import bittensor
import rich
from fastapi import Body, Depends, FastAPI, Header, HTTPException

from btvep.config import Config
from btvep.constants import DEFAULT_UID
from btvep.db.request import Request
from btvep.db.tables import create_all as create_all_tables
from btvep.db.utils import DB_PATH
from btvep.fastapi_dependencies import InitializeRateLimiting, VerifyAndLimit, get_db
from btvep.btvep_models import ChatResponse, Message
from btvep.validator_prompter import ValidatorPrompter
from btvep.admin_api import (
    router as admin_router,
)  # composed router from the admin module

create_all_tables()
config = Config().load().validate()

# Give info around configuration at server start
print("Config:")
rich.print_json(config.to_json(hide_mnemonic=True))
print("Using SQLite database at", DB_PATH)

# Initialize the validator prompter for bittensor
hotkey = bittensor.Keypair.create_from_mnemonic(config.hotkey_mnemonic)
validator_prompter = ValidatorPrompter(hotkey, DEFAULT_UID)


app = FastAPI()

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
    if response.is_success:
        Request.create(
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
