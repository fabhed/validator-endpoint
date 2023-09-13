from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, Header

from btvep.api.dependencies import authenticate_api_key
from btvep.btvep_models import ChatResponse, Message
from btvep.chat_helpers import (
    process_responses,
    query_network,
    raise_for_all_failed_responses,
    setup_async_loop,
)
from btvep.constants import COST, DEFAULT_UIDS
from btvep.db.api_keys import ApiKey
from btvep.db.api_keys import update as update_api_key

router = APIRouter()


@router.post("/chat")
async def chat(
    authorization: Annotated[str | None, Header()] = None,
    uids: Annotated[List[int] | None, Body()] = DEFAULT_UIDS,
    top_n: Annotated[
        int | None,
        Body(
            description="Query top miners based on incentive in the network. If set to for example 5, the top 5 miners will be sent the request. This parameter takes precedence over the uids parameter."
        ),
    ] = None,
    messages: Annotated[List[Message] | None, Body()] = None,
    api_key: ApiKey = Depends(authenticate_api_key),
) -> ChatResponse:
    setup_async_loop()
    prompter_responses = await query_network(messages, uids, top_n)
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
