import bittensor


class ValidatorPrompter:
    def __init__(self, wallet_name, hotkey_name, netuid=1):
        self.metagraph: bittensor.metagraph = bittensor.metagraph(netuid)
        self.wallet = bittensor.wallet(name=wallet_name, hotkey=hotkey_name)
        self._set_dendrite(0)  # default axon

    def _set_dendrite(self, uid):
        axon = self.metagraph.axons[uid]
        self.dendrite = bittensor.text_prompting(keypair=self.wallet.hotkey, axon=axon)

    def query_network(self, messages, uid=None):
        roles = [el["role"] for el in messages]
        messages = [el["content"] for el in messages]
        if uid is not None:
            self._set_dendrite(uid)
        out = self.dendrite(roles=roles, messages=messages)
        return out
