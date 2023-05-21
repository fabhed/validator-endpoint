import asyncio
from typing import Annotated, Dict, List, Union

import bittensor
from decouple import config
from fastapi import Body, FastAPI, Header

from validator_prompter import ValidatorPrompter

mnemomic = config("HOTKEY_MNEMONIC")
hotkey = bittensor.Keypair.create_from_mnemonic(mnemomic)
validator_prompter = ValidatorPrompter(hotkey)

app = FastAPI()


@app.get("/")
def read_root():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list


@app.post("/chat")
def chat(
    authorization: Annotated[str | None, Header()] = None,
    uid: Annotated[int | None, Body()] = 0,
    messages: Annotated[List[Dict[str, str]] | None, Body()] = None,
):
    # An event loop for the thread is required by the bittensor library
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    response = validator_prompter.query_network(messages=messages, uid=uid)
    if response.is_success:
        return {
            "message": {"role": "assistant", "content": response.completion},
            "responder_hotkey": response.dest_hotkey,
        }
    else:
        return {"error": True, "message": response.return_message}


# start with uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
