from typing import List
import bittensor

from btvep.types import Message

DEFAULT_UID = 0  # default to the first miner for now


class ValidatorPrompter:
    def __init__(self, hotkey: bittensor.Keypair, netuid=1):
        self.metagraph: bittensor.metagraph = bittensor.metagraph(netuid)
        self.hotkey = hotkey
        # Create a defualt dendrite instance we can use if uid is not specified
        self.default_dendrite = self._get_dendrite(DEFAULT_UID)

    def _get_dendrite(self, uid):
        axon = self.metagraph.axons[uid]
        return bittensor.text_prompting(keypair=self.hotkey, axon=axon)

    def query_network(self, messages: List[Message], uid=None):
        roles = [el.role for el in messages]
        messages = [el.content for el in messages]
        dendrite = (
            self._get_dendrite(uid) if uid is not DEFAULT_UID else self.default_dendrite
        )

        out = dendrite(roles=roles, messages=messages)
        return out
