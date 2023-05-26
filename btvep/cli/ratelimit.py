from typing import Annotated
import rich
from rich.table import Table


import typer

from btvep.config import Config
from btvep.db import api_keys
from btvep.types import RateLimit

help_text = f"""
    Global Rate limit settings. Rate limits requires a Redis server.
    Global rate limits can be overridden by setting rate limits on an api key.
    """
app = typer.Typer(help=help_text)


def print_ratelimit_table():
    config = Config().load()
    # Print as a table with index isntead
    table = Table(title="Current global rate limits")
    table.add_column("Index")
    table.add_column("Requests")
    table.add_column("Per x seconds")

    for i, rate_limit in enumerate(config.global_rate_limits):
        table.add_row(
            str(i),
            str(rate_limit["times"]),
            str(rate_limit["seconds"]),
        )
    rich.print(table)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(ctx: typer.Context):
    # check ctx
    if ctx.invoked_subcommand is None:
        print(help_text)
        print_ratelimit_table()


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
    Set the redis url to use for rate limiting. Defaults to redis://localhost\n
    Alias for `btvep config set redis_url <url>`\n
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
):
    """
    Add a global rate limit. This will be part of the default rate limits for all api keys without specific rate limits.
    """
    config = Config().load()
    rate_limit = RateLimit(times=times, seconds=seconds)
    config.global_rate_limits.append(rate_limit)
    config.save()
    print_ratelimit_table()


@app.command()
def delete(
    index: Annotated[
        int,
        typer.Argument(
            help="The index (starts at 0) of the rate limit to delete.",
        ),
    ],
):
    """
    Delete a global rate limit.
    """
    config = Config().load()
    config.global_rate_limits.pop(index)
    config.save()
    print_ratelimit_table()
