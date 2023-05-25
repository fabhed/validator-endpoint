from typing import Annotated

import typer

from btvep.config import Config
from btvep.db import api_keys

app = typer.Typer(
    help=f"""
    Update and read config values. Config values available:\n
    \n
    \t- hotkey_mnemonic\n\n
    The hotkey mnemonic for the validator. This is required as the validator will be signing the prompts to miners.\n\n
    Example usage:\n
    - btvep config set hotkey_mnemonic "my mnemonic"\n
    - btvep config get hotkey_mnemonic

"""
)


@app.callback(invoke_without_command=True)
def main():
    print("Manage config values. Use --help for more info.\n")
    print("Current config values:")
    config = Config().load()
    print(config)


@app.command()
def set(
    key: Annotated[
        str,
        typer.Argument(
            help="The config key to set.",
        ),
    ],
    value: Annotated[
        str,
        typer.Argument(
            help="The config value to set.",
        ),
    ],
):
    """
    Set a config value.
    """
    config = Config().load()

    # handle mnemonic
    # This will currently overwrite the entire .env file.
    # TODO: Add a better way to save config values. Maybe a json file or in db.
    if key == "hotkey_mnemonic":
        # write to .env relative to this file
        config.hotkey_mnemonic = value
        config.save()
    else:
        # Raise error with typer
        raise typer.BadParameter(f"""Unknown config key: {key}""")
    print(f"""Updated {key} """)


@app.command()
def get(
    key: Annotated[
        str,
        typer.Argument(
            help="The config key to get.",
        ),
    ] = None,
):
    """
    Prints a config value.
    """
    config = Config().load()

    # handle mnemonic
    if key == "hotkey_mnemonic":
        print(config.hotkey_mnemonic)
    else:
        # Raise error with typer
        raise typer.BadParameter(f"""Unknown config key: {key}""")
