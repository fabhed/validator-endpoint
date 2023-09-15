from typing import Annotated
import rich
from rich.markdown import Markdown

import typer

from btvep.config import Config, CONFIG_PATH, cast_str_to_bool

app = typer.Typer(
    help=f"""
Update and read config values. Config values are stored in a json file at {CONFIG_PATH}

General Config values available:

- hotkey_mnemonic - The hotkey mnemonic for the validator. This is required as the validator will be signing the prompts to miners.
- openai_filter_enabled - Whether to use OpenAI's content filter. If enabled, the openai_api_key will be used.
- openai_api_key - The OpenAI API key to use for the content filter.

Rate Limiting Config values available:

- rate_limiting_enabled - Whether to enable rate limiting. If enabled, the global_rate_limits will be used.
- redis_url - The redis url to use for rate limiting.
- global_rate_limits - A list of rate limits. Prefer to use btvep ratelimit to manage rate limits.


Example usage:

1. Set hotkey_mnemonic:
    `btvep config set hotkey_mnemonic "my_validators_secret_mnemonic_phrase_here"`

2. Get hotkey_mnemonic:
    `btvep config get hotkey_mnemonic`
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
        # cast to correct type
        if type(config.__dict__[key]) == bool:
            value = cast_str_to_bool(value)
        config.__dict__[key] = value
        config.save()
    else:
        # Raise error with typer
        raise typer.BadParameter(f"""Unknown config key: {key}""")
    print(f"""{key} = {config.load().__dict__[key]}""")


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

    # support all config keys with __dict__
    if key in config.__dict__:
        print(config.__dict__[key])
    else:
        # Raise error with typer
        raise typer.BadParameter(f"""Unknown config key: {key}""")
