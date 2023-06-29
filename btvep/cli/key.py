from datetime import datetime
from typing import Annotated
import dateparser
import rich
import typer

from btvep.db import api_keys

app = typer.Typer(help="Manage API keys.")


@app.callback(no_args_is_help=True)
def main():
    pass


@app.command()
def create(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="The name of the API key.",
        ),
    ] = None,
    valid_until: Annotated[
        int,
        typer.Option(
            "--valid-until",
            "-v",
            help="The unix timestamp when the API key expires. Defaults to -1 which means that the key never expires.",
        ),
    ] = -1,
    credits: Annotated[
        int,
        typer.Option(
            "--credits",
            "-c",
            help="The number of credits the API key has. -1 means unlimited.",
        ),
    ] = -1,
    enabled: Annotated[
        bool,
        typer.Option(
            "--enable/--disable",
            "-e/-d",
            help="Whether the API key is enabled or not. Disabled keys cannot make requests.",
        ),
    ] = True,
):
    """
    Create a new API key.
    """
    api_key = api_keys.insert(
        name=name, valid_until=valid_until, credits=credits, enabled=enabled
    )
    print(api_key)


@app.command()
def list():
    """
    List all API keys.
    """
    all = api_keys.get_all()
    print(api_keys.ApiKey.tabulate(all))


@app.command()
def delete(
    query: Annotated[
        str,
        typer.Argument(
            help="The API key to delete. Can be specified by either the key or its numerical id.",
        ),
    ]
):
    """
    Deletes an API key.
    """
    count = api_keys.delete(query)

    if count == 0:
        print(f"Key {query} not found")
    else:
        print(f"Deleted key {query}")


# edit
@app.command()
def edit(
    query: Annotated[
        str,
        typer.Argument(
            help="The API key to edit. Can be specified by either the key or its numerical id.",
        ),
    ],
    # Values as options
    api_key_hint: str = typer.Option(None, "--api_key_hint", "-k"),
    name: str = typer.Option(None, "--name", "-n"),
    request_count: int = typer.Option(None, "--request_count", "-r"),
    valid_until: str = typer.Option(
        None,
        "--valid_until",
        "-u",
        help="""
        When the API key expires.
        Set to false to disable expiration.
        You can specify the expiry in natural language (e.g. 'in 1 month', 'in 10 days', 'December 2025', 'next year', 'tomorrow', 'next week', etc.)
        or as a date (e.g. '2025-01-01').
        or as an epoch timestamp (e.g. '1735603200')
        Parsing of relative dates will be relative to the current date but ignore the current time of day.
        """,
    ),
    credits: int = typer.Option(None, "--credits", "-c"),
    enabled: Annotated[
        bool,
        typer.Option(
            "--enable/--disable",
            "-e/-d",
            show_default=False,
            help="Enable or disable the API key.",
        ),
    ] = None,
):
    """
    Edit an API key.
    """

    parsed_valid_until = None
    if valid_until is not None:
        if valid_until.lower() == "false" or valid_until.lower() == "-1":
            parsed_valid_until = -1
        else:
            # https://dateparser.readthedocs.io/en/latest/
            parsed_valid_until = dateparser.parse(
                valid_until,
                settings={
                    "PREFER_DATES_FROM": "future",
                    "DATE_ORDER": "YMD",
                    "PREFER_DAY_OF_MONTH": "first",
                    # Option is not yet released, but saw it in a github issue https://github.com/scrapinghub/dateparser/pull/1146
                    # "PREFER_MONTH_OF_YEAR": "first",
                    # Relative base for current date but 0 hours, 0 minutes, 0 seconds
                    "RELATIVE_BASE": datetime.now().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    ),
                },
            )
            if parsed_valid_until is None:
                raise typer.BadParameter(
                    f"Could not parse date '{valid_until}'. Try another format."
                )
            # Rich formatt the date
            rich.print(
                f"""Parsed date as [bold]{parsed_valid_until.date()} {parsed_valid_until.time()}[/bold]"""
            )
            parsed_valid_until = int(parsed_valid_until.timestamp())

    api_keys.update(
        query,
        api_key_hint,
        name,
        request_count,
        parsed_valid_until,
        credits,
        enabled,
    )
    print(api_keys.get(query))
