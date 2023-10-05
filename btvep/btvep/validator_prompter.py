import asyncio
import logging
from typing import List, Optional

import bittensor as bt
from bittensor import Keypair, metagraph,  Keypair #prompting,text_prompting

from btvep.btvep_models import Message
from btvep.constants import DEFAULT_NETUID
from btvep.metagraph import MetagraphSyncer

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

import pydantic
import time
import torch
from typing import List
import bittensor as bt
from starlette.responses import StreamingResponse


class Prompting(bt.Synapse):
    """
    The Prompting subclass of the Synapse class encapsulates the functionalities related to prompting scenarios.

    It specifies three fields - `roles`, `messages` and `completion` - that define the state of the Prompting object.
    The `roles` and `messages` are read-only fields defined during object initialization, and `completion` is a mutable
    field that can be updated as the prompting scenario progresses.

    The Config inner class specifies that assignment validation should occur on this class (validate_assignment = True),
    meaning value assignments to the instance fields are checked against their defined types for correctness.

    Attributes:
        roles (List[str]): A list of roles in the prompting scenario. This field is both mandatory and immutable.
        messages (List[str]): A list of messages in the prompting scenario. This field is both mandatory and immutable.
        completion (str): A string that captures completion of the prompt. This field is mutable.
        required_hash_fields List[str]: A list of fields that are required for the hash.

    Methods:
        deserialize() -> "Prompting": Returns the instance of the current object.


    The `Prompting` class also overrides the `deserialize` method, returning the
    instance itself when this method is invoked. Additionally, it provides a `Config`
    inner class that enforces the validation of assignments (`validate_assignment = True`).

    Here is an example of how the `Prompting` class can be used:

    ```python
    # Create a Prompting instance
    prompt = Prompting(roles=["system", "user"], messages=["Hello", "Hi"])

    # Print the roles and messages
    print("Roles:", prompt.roles)
    print("Messages:", prompt.messages)

    # Update the completion
    model_prompt =... # Use prompt.roles and prompt.messages to generate a prompt
    for your LLM as a single string.
    prompt.completion = model(model_prompt)

    # Print the completion
    print("Completion:", prompt.completion)
    ```

    This will output:
    ```
    Roles: ['system', 'user']
    Messages: ['You are a helpful assistant.', 'Hi, what is the meaning of life?']
    Completion: "The meaning of life is 42. Deal with it, human."
    ```

    This example demonstrates how to create an instance of the `Prompting` class, access the
    `roles` and `messages` fields, and update the `completion` field.
    """

    class Config:
        """
        Pydantic model configuration class for Prompting. This class sets validation of attribute assignment as True.
        validate_assignment set to True means the pydantic model will validate attribute assignments on the class.
        """

        validate_assignment = True

    def deserialize(self) -> "Prompting":
        """
        Returns the instance of the current Prompting object.

        This method is intended to be potentially overridden by subclasses for custom deserialization logic.
        In the context of the Prompting class, it simply returns the instance itself. However, for subclasses
        inheriting from this class, it might give a custom implementation for deserialization if need be.

        Returns:
            Prompting: The current instance of the Prompting class.
        """
        return self

    roles: List[str] = pydantic.Field(
        ...,
        title="Roles",
        description="A list of roles in the Prompting scenario. Immuatable.",
        allow_mutation=False,
    )

    messages: List[str] = pydantic.Field(
        ...,
        title="Messages",
        description="A list of messages in the Prompting scenario. Immutable.",
        allow_mutation=False,
    )

    completion: str = pydantic.Field(
        "",
        title="Completion",
        description="Completion status of the current Prompting object. This attribute is mutable and can be updated.",
    )

    required_hash_fields: List[str] = pydantic.Field(
        ["messages"],
        title="Required Hash Fields",
        description="A list of required fields for the hash.",
        allow_mutation=False,
    )
    is_completion: bool = False


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
                if respond_on_first_success and result["dendrite_response"].is_completion:
                    for task in tasks:
                        task.cancel()  # Cancel all other tasks
                    return results  # Return the successful result
        return results

    def _create_tasks(self, uids, roles, messages, uid_idx, in_parallel, timeout):
        tasks = []
        for _ in range(min(in_parallel, len(uids) - uid_idx)):
            uid = uids[uid_idx]
            uid_idx += 1
            task = asyncio.create_task(
                self._query_uid(roles, messages, uid, timeout)
            )
            tasks.append(task)
        return tasks

    async def _query_uid(self, roles, messages, uid, timeout=None):
        # Avoid overwriting the default timeout of bittensor if timeout is None
        logging.info(f"Querying uid {uid}")
        timeout_arg = {"timeout": timeout} if timeout is not None else {}
        axons = [self.metagraph_syncer.metagraph.axons[uid]]

        synapse = Prompting(roles=roles, messages=messages)

        result = self.dendrite.query(
            axons,
            synapse,
            deserialize=False
        )
        result = result[0]
        if result.completion:
            result.is_completion=True
        response = {"uid": uid, "dendrite_response": result}

        return response
