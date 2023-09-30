from typing import Annotated, List
from fastapi import APIRouter, Body, Depends, Header
from btvep.api.dependencies import authenticate_user
from btvep.chat_helpers import (
    process_responses,
    query_network,
    raise_for_all_failed_responses,
    setup_async_loop,
)

from btvep.constants import DEFAULT_UIDS
from btvep.btvep_models import (
    ChatResponse,
    Message,
)
from btvep.db.user import User

router = APIRouter()


@router.post("/conversation")
async def conversation(
    authorization: Annotated[str | None, Header()] = None,
    uids: Annotated[List[int] | None, Body()] = DEFAULT_UIDS,
    top_n: Annotated[
        int | None,
        Body(
            description="Query top miners based on incentive in the network. If set to for example 5, the top 5 miners will be sent the request. This parameter takes precidence over the uids parameter."
        ),
    ] = None,
    in_parallel: Annotated[int | None, Body()] = None,
    attempts: Annotated[int | None, Body()] = None,
    messages: Annotated[List[Message] | None, Body()] = None,
    user: User = Depends(authenticate_user),
) -> ChatResponse:
    setup_async_loop()
    prompter_responses = await query_network(
        messages, uids, top_n, in_parallel, attempts
    )
    choices, failed_responses, all_failed = process_responses(
        prompter_responses, messages, authorization
    )
    print(all_failed, choices, failed_responses)

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
