from typing import Annotated
import json
import rich
from rich.table import Table


import typer

from btvep.config import Config
from btvep.db import api_keys
from btvep.btvep_models import RateLimitEntry

help_text = f"""
    Global & API Key-specific Rate limit settings. Rate limits requires a Redis server.
    Global rate limits can be overridden by setting rate limits on an api key.
    """
app = typer.Typer(help=help_text)


def print_ratelimit_table(
    title: str, rate_limits: list[RateLimitEntry] = Config().load().global_rate_limits
):
    # Print as a table with index isntead
    table = Table(title=title)
    table.width = 80
    table.add_column("Index")
    table.add_column("Requests")
    table.add_column("Per x seconds")

    for i, rate_limit in enumerate(rate_limits):
        table.add_row(
            str(i),
            str(rate_limit["times"]),
            str(rate_limit["seconds"]),
        )
    rich.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    api_key: Annotated[
        str,
        typer.Option(
            "--key",
            "-k",
            help="The API key (ID or the key itself) to view rate limits for.",
        ),
    ] = None,
):
    if ctx.invoked_subcommand is None:
        if ctx.params["api_key"]:
            api_key = api_keys.get(api_key)
            if not api_key:
                raise typer.BadParameter(f"API key {api_key.api_key} not found.")
            if not api_key.rate_limits:
                typer.echo(f"API key {api_key.api_key} has no rate limits set.")
                return
            rate_limits = json.loads(api_key.rate_limits)
            print_ratelimit_table(
                f"Rate limits for API key {api_key.api_key}", rate_limits
            )

        else:
            print_ratelimit_table("Current global rate limits")
            print(ctx.get_help())


@app.command()
def status():
    """
    If rate limiting is enabled or not.
    """
    config = Config().load()
    print(
        f"""Rate limiting is {'enabled' if config.rate_limiting_enabled else 'disabled'}"""
    )


@app.command()
def enable():
    """
    Enable rate limiting.
    """
    config = Config().load()
    config.rate_limiting_enabled = True
    config.save()


@app.command()
def disable():
    """
    Disable rate limiting.
    Alias for btvep config set rate_limiting_enabled False
    """
    config = Config().load()
    config.rate_limiting_enabled = False
    config.save()


@app.command()
def set_redis_url(
    url: Annotated[
        str,
        typer.Argument(
            help="The redis url to set.",
        ),
    ],
):
    """
    Set the redis url to use for rate limiting. Defaults to redis://localhost
    Alias for btvep config set redis_url <url>
    """
    config = Config().load()
    config.redis_url = url
    config.save()


@app.command()
def add(
    times: Annotated[
        int,
        typer.Argument(
            help="How many times to allow in the given time period.",
        ),
    ],
    seconds: Annotated[
        int,
        typer.Argument(
            help="The time period in seconds.",
        ),
    ],
    api_key: Annotated[
        str,
        typer.Option(
            "--key",
            "-k",
            help="The api key (ID or the key itself) to add the rate limit to. If not specified, the rate limit will be added to the global rate limits.",
        ),
    ] = None,
):
    """
    Add a rate limit. Global rate limits do not apply to API keys with their own rate limits.
    """
    config = Config().load()
    rate_limit = RateLimitEntry(times=times, seconds=seconds)
    if api_key:
        # Add to the api key
        api_key = api_keys.get(api_key)
        if api_key is None:
            raise typer.BadParameter(f"API key {api_key} does not exist")

        # Handle empty rate limits, or load existing json
        if api_key.rate_limits is None:
            api_key.rate_limits = []
        else:
            api_key.rate_limits = json.loads(api_key.rate_limits)

        api_key.rate_limits.append(rate_limit.dict())
        rate_limits = api_key.rate_limits
        # Save
        api_key.rate_limits = json.dumps(api_key.rate_limits)
        api_key.save()
        print_ratelimit_table(f"Rate limits for API key {api_key.api_key}", rate_limits)
    else:
        # No key specified, add to global rate limits
        config.global_rate_limits.append(rate_limit.dict())
        config.save()
        print_ratelimit_table("Current global rate limits", config.global_rate_limits)


@app.command()
def delete(
    index: Annotated[
        int,
        typer.Argument(
            help="The index (starts at 0) of the rate limit to delete.",
        ),
    ],
    api_key: Annotated[
        str,
        typer.Option(
            "--key",
            "-k",
            help="The api key (ID or the key itself) to add the rate limit to. If not specified, the rate limit will be removed from the global rate limits.",
        ),
    ] = None,
):
    """
    Delete a rate limit.
    """
    config = Config().load()

    if api_key:
        # Delete from the api key
        api_key = api_keys.get(api_key)
        if api_key is None:
            raise typer.BadParameter(f"API key {api_key} does not exist")

        # Handle empty rate limits, or load existing json
        if api_key.rate_limits is None:
            api_key.rate_limits = []
        else:
            api_key.rate_limits = json.loads(api_key.rate_limits)

        try:
            api_key.rate_limits.pop(index)
        except IndexError:
            raise typer.BadParameter(f"Rate limit with index {index} does not exist.")

        rate_limits = (
            api_key.rate_limits
        )  # Save to display before converting to json string
        api_key.rate_limits = json.dumps(api_key.rate_limits)
        api_key.save()
        print_ratelimit_table(f"Rate limits for API key {api_key.api_key}", rate_limits)
    else:
        try:
            config.global_rate_limits.pop(index)
        except IndexError:
            raise typer.BadParameter(f"Rate limit with index {index} does not exist.")
        config.save()
        print_ratelimit_table("Current global rate limits", config.global_rate_limits)
