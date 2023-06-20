from typing import Annotated

DEFAULT_UID: Annotated[str, "Neuron UID to use if none is specified"] = 0
DEFAULT_NETUID: Annotated[str, "NETUID to prompt"] = 1
COST: Annotated[str, "Credit Cost per request"] = 1
