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


def apply_default_query_strategy(
    uids: List[int] | None, top_n: int | None, default_query_strategy: str | None
) -> (List[int] | None, int | None):
    """
    Apply the default query strategy if neither uids nor top_n are specified.
    If no strategy is set, it returns DEFAULT_UIDS.

    Args:
    - uids: List of user ids or None.
    - top_n: Top n users or None.
    - default_query_strategy: The default strategy string.

    Returns:
    - Tuple containing modified uids and top_n.
    """
    if uids is None and top_n is None:
        if default_query_strategy:
            strategy = default_query_strategy.split(":")
            if strategy[0] == "top_n":
                top_n = int(strategy[1])
            elif strategy[0] == "uids":
                uids = list(map(int, strategy[1].split(",")))
        else:
            uids = DEFAULT_UIDS

    return uids, top_n


@router.post("/chat")
async def chat(
    authorization: Annotated[str | None, Header()] = None,
    uids: Annotated[List[int] | None, Body()] = None,
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
    uids, top_n = apply_default_query_strategy(
        uids, top_n, api_key.default_query_strategy
    )
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
