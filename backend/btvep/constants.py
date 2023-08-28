from typing import Annotated, List

DEFAULT_UIDS: Annotated[
    List[int], "Neuron UIDs to use if none is specified in request."
] = [0]
DEFAULT_NETUID: Annotated[str, "NETUID to prompt"] = 1
COST: Annotated[str, "Credit Cost per request"] = 1
