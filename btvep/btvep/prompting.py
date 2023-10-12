import bittensor as bt
import pydantic
from typing import List

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
    dest_hotkey: str = ''
    return_message: str = ''
    elapsed: float = None
    src_version: int = bt.__version_as_int__
    dest_version: int = None
    return_code: int = None
