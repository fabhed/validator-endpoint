import asyncio
import logging
from typing import List, Optional

import bittensor as bt
from bittensor import Keypair, metagraph, Keypair  # prompting,text_prompting

from btvep.btvep_models import Message
from btvep.constants import DEFAULT_NETUID
from btvep.metagraph import MetagraphSyncer
from btvep.prompting import Prompting

# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


class MetagraphNotSyncedException(Exception):
    pass


class ValidatorPrompter:
    """
    ValidatorPrompter is a class that allows us to prompt the bittensor network
    Initialisation of this class is expensive because of the metagraph,
    so we want initialize it once and then reuse the instance for api requests.
    """

    _instance = None
    _initialized_with: str | None = (
        None  # Store the mnemonic used to initialize the instance
    )

    def __new__(cls, hotkey_mnemonic: str | None = None):
        if cls._instance is None:
            cls._instance = super(ValidatorPrompter, cls).__new__(cls)
            # initialization logic for the first instance
            cls._initialized_with = hotkey_mnemonic
            if hotkey_mnemonic is None:
                raise ValueError(
                    "ValidatorPrompter must be initialized with a mnemonic!"
                )
            cls._instance._initialize(hotkey_mnemonic)
        elif hotkey_mnemonic is not None and cls._initialized_with != hotkey_mnemonic:
            raise ValueError(
                "ValidatorPrompter has already been initialized with a different mnemonic!"
            )
        return cls._instance

    def _initialize(self, hotkey_mnemonic: str):
        self.metagraph_syncer = MetagraphSyncer(DEFAULT_NETUID)
        self.metagraph_syncer.start_sync_thread()
        self.hotkey = Keypair.create_from_mnemonic(hotkey_mnemonic)
        self.dendrite = bt.dendrite(wallet=self.hotkey)

    def __init__(self, *args, **kwargs):
        pass

    async def query_network(
        self,
        messages: List[Message],
        uids: Optional[List[int]] = None,
        top_n: Optional[int] = None,
        in_parallel: Optional[int] = None,
        timeout: Optional[int] = None,
        respond_on_first_success: bool = True,
    ):
        if in_parallel is not None and in_parallel < 1:
            raise ValueError("in_parallel must be at least 1")

        self._validate_metagraph()
        roles, messages = self._prepare_messages(messages)

        if top_n is not None:
            uids = self._get_top_uids(top_n)
        elif uids is None:
            raise ValueError("Either uids or top_n must be specified")

        in_parallel = in_parallel or len(
            uids
        )  # Default to processing all uids in parallel
        return await self._process_in_parallel(
            uids, roles, messages, in_parallel, timeout, respond_on_first_success
        )

    def _validate_metagraph(self):
        if self.metagraph_syncer.metagraph is None:
            raise MetagraphNotSyncedException()

    def _prepare_messages(self, messages: List[Message]):
        roles = [el.role for el in messages]
        messages = [el.content for el in messages]
        return roles, messages

    def _get_top_uids(self, top_n: int):
        _, indices = self.metagraph_syncer.metagraph.incentive.sort(descending=True)
        return indices[:top_n].tolist()

    async def _process_in_parallel(
        self, uids, roles, messages, in_parallel, timeout, respond_on_first_success
    ):
        results = []
        uid_idx = 0

        while uid_idx < len(uids):
            tasks = self._create_tasks(
                uids, roles, messages, uid_idx, in_parallel, timeout
            )
            uid_idx += len(tasks)

            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)
                if (
                    respond_on_first_success
                    and result["dendrite_response"].is_completion
                ):
                    for task in tasks:
                        task.cancel()  # Cancel all other tasks
                    return results  # Return the successful result
        return results

    def _create_tasks(self, uids, roles, messages, uid_idx, in_parallel, timeout):
        tasks = []
        for _ in range(min(in_parallel, len(uids) - uid_idx)):
            uid = uids[uid_idx]
            uid_idx += 1
            task = asyncio.create_task(self._query_uid(roles, messages, uid, timeout))
            tasks.append(task)
        return tasks

    async def _query_uid(self, roles, messages, uid, timeout=None):
        # Avoid overwriting the default timeout of bittensor if timeout is None

        logging.info(f"Querying uid {uid}")
        timeout_arg = {"timeout": timeout} if timeout is not None else {}
        axon = self.metagraph_syncer.metagraph.axons[uid]

        synapse = Prompting(roles=roles, messages=messages)

        result = self.dendrite.query([axon], synapse, deserialize=False)
        result = result[0]
        if result.dendrite.process_time:
            result.elapsed = result.dendrite.process_time
        else:
            result.elapsed = result.timeout
        result.dest_hotkey = axon.hotkey
        result.return_code = result.dendrite.status_code
        result.return_message = result.dendrite.status_message
        if result.completion:
            print('**COMPLETION',result.completion)
            result.is_completion = True
        else:
            # Case empty dentrite response
            if result.dendrite.status_code == 200:
                result.return_message = "Empty response"

        response = {"uid": uid, "dendrite_response": result}

        return response
