from typing import Annotated
import rich
from rich.markdown import Markdown

import typer

from btvep.config import Config
from btvep.db import api_keys

app = typer.Typer(
    help="""
Update and read config values. Config values available:

- **hotkey_mnemonic** The hotkey mnemonic for the validator. This is required as the validator will be signing the prompts to miners.

-

**Example usage:**

- btvep config set hotkey_mnemonic "my mnemonic"

- btvep config get hotkey_mnemonic
""",
)


@app.callback(
    invoke_without_command=True,
)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print("Manage config values. Use --help for more info.\n")
        rich.print("[bold]Current config values:[/bold]")
        config = Config().load()
        rich.print_json(config.to_json())


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

    # support all config keys with __dict__
    if key in config.__dict__:
        config.__dict__[key] = value
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
