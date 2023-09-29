import asyncio
from typing import List, Optional

from bittensor import Keypair, metagraph, text_prompting, Keypair

from btvep.btvep_models import Message
from btvep.constants import DEFAULT_NETUID
from btvep.metagraph import MetagraphSyncer


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

    def __init__(self, *args, **kwargs):
        pass

    def _get_dendrite(self, uid):
        if self.metagraph_syncer.metagraph is None:
            raise MetagraphNotSyncedException()
        axon = self.metagraph_syncer.metagraph.axons[uid]
        return text_prompting(keypair=self.hotkey, axon=axon)

    async def query_network(
        self, messages: List[Message], uids: List[int], top_n: Optional[int] = None,
        in_parallel: Optional[int] = None, attempts: Optional[int] = None
    ):
        if self.metagraph_syncer.metagraph is None:
            raise MetagraphNotSyncedException()

        roles = [el.role for el in messages]
        messages = [el.content for el in messages]
        if in_parallel is not None:
            results=[]
            count_attempts = 0
            max_attempts = 5 #attempts default value
            if attempts is not None :
                max_attempts = attempts
            _, indices = self.metagraph_syncer.metagraph.incentive.sort(descending=True)
            uids = indices[:(max_attempts*in_parallel)].tolist()
            stop = False
            while stop==False and count_attempts != max_attempts:
                tasks = []
                for uid in uids[count_attempts:count_attempts+in_parallel]:
                    dendrite = self._get_dendrite(uid)
                    task = asyncio.create_task(self._query_uid(dendrite, roles, messages, uid))
                    tasks.append(task)
                    for completed_task in asyncio.as_completed(tasks, timeout=10):
                        response = await completed_task
                        results.append(response)
                        dendrite_response = response["dendrite_response"]
                        if dendrite_response.is_success:
                            stop==True
                            tasks.clear()
                            return results
                count_attempts +=1
            return results
        else:
            if top_n is not None:
                _, indices = self.metagraph_syncer.metagraph.incentive.sort(descending=True)
                uids = indices[:top_n].tolist()

            tasks = []
            for uid in uids:
                dendrite = self._get_dendrite(uid)
                task = asyncio.create_task(self._query_uid(dendrite, roles, messages, uid))
                tasks.append(task)

            # execute all requests in parallel
            results = await asyncio.gather(*tasks)
            return results

    async def _query_uid(self, dendrite, roles, messages, uid):
        result = await dendrite.async_forward(roles=roles, messages=messages)
        return {"uid": uid, "dendrite_response": result}
