import asyncio
from typing import List

from bittensor import Keypair, metagraph, text_prompting

from btvep.btvep_models import Message
from btvep.metagraph import MetagraphSyncer


class MetagraphNotSyncedException(Exception):
    pass


class ValidatorPrompter:
    """
    ValidatorPrompter is a class that allows us to prompt the bittensor network
    Initialisation of this class is expensive because of the metagraph,
    so we want initialize it once and then reuse the instance for api requests.
    """

    def __init__(self, hotkey: Keypair, metagraph_syncer: MetagraphSyncer):
        self.metagraph_syncer: MetagraphSyncer = metagraph_syncer
        self.hotkey = hotkey

    def _get_dendrite(self, uid):
        if self.metagraph_syncer.metagraph is None:
            raise MetagraphNotSyncedException()
        axon = self.metagraph_syncer.metagraph.axons[uid]
        return text_prompting(keypair=self.hotkey, axon=axon)

    async def query_network(self, messages: List[Message], uids: List[int]):
        if self.metagraph_syncer.metagraph is None:
            raise MetagraphNotSyncedException()
        roles = [el.role for el in messages]
        messages = [el.content for el in messages]

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
