import time
from typing import List
from bittensor import Keypair, metagraph, text_prompting

from btvep.types import Message


class ValidatorPrompter:
    """
    ValidatorPrompter is a class that allows us to prompt the bittensor network
    Initialisation of this class is expensive because of the metagraph,
    so we want initialize it once and then reuse the instance for api requests.
    """

    def __init__(self, hotkey: Keypair, netuid: int):
        self.metagraph: metagraph = metagraph(netuid)
        self.hotkey = hotkey

    def _get_dendrite(self, uid):
        axon = self.metagraph.axons[uid]
        return text_prompting(keypair=self.hotkey, axon=axon)

    def query_network(self, messages: List[Message], uid=None):
        roles = [el.role for el in messages]
        messages = [el.content for el in messages]
        dendrite = self._get_dendrite(uid)

        out = dendrite(roles=roles, messages=messages)
        return out
