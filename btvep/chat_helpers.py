import asyncio
import json
from typing import Union, List, Tuple, Dict
from fastapi import HTTPException
from enum import Enum

from btvep.btvep_models import (
    ChatResponseChoice,
    FailedMinerResponse,
    Message,
)

from btvep.validator_prompter import MetagraphNotSyncedException, ValidatorPrompter
from bittensor.utils.codes import code_to_string
import uuid
from btvep.db.request import Request


# Setting up Async Loop
def setup_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


# Querying the Network
async def query_network(
    validator_prompter: ValidatorPrompter,
    messages: List[Message],
    uids: List[int],
    top_n: int,
) -> dict:
    try:
        return await validator_prompter.query_network(
            messages=messages, uids=uids, top_n=top_n
        )
    except MetagraphNotSyncedException as e:
        raise HTTPException(
            detail="Metagraph is not synced yet. Please try again later.",
            status_code=500,
        ) from e


# Processing the Responses
def process_responses(
    prompter_responses: dict, messages: List[Message], authorization: str
) -> Tuple[List[ChatResponseChoice], List[FailedMinerResponse]]:
    choices = []
    failed_responses = []
    success_index = 0
    failed_index = 0
    for p_response in prompter_responses:
        dendrite_res = p_response["dendrite_response"]
        uid = p_response["uid"]

        return_code = (
            dendrite_res.return_code.value
            if isinstance(type(dendrite_res.return_code), type(Enum))
            else dendrite_res.return_code
        )
        return_code_str = code_to_string(return_code)

        Request.create(
            is_api_success=True,
            api_request_id=str(uuid.uuid4()),
            prompt=json.dumps([message.dict() for message in messages]),
            user_id=authorization.split(" ")[
                1
            ],  # Assuming API key is also passed in the same format.
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

    all_failed = len(failed_responses) == len(prompter_responses)
    return choices, failed_responses, all_failed


class ChatResponseException(Exception):
    def __init__(self, detail: str, failed_responses: List[Dict], status_code: int):
        self.detail = detail
        self.failed_responses = failed_responses
        self.status_code = status_code


# Raise Exception if all responses fail
def raise_for_all_failed_responses(failed_responses: List[FailedMinerResponse]):
    raise ChatResponseException(
        status_code=502,  # Bad Gateway
        detail="All miner responses have failed.",
        failed_responses=failed_responses,
    )
