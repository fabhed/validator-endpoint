from typing import Annotated
import typer

from btvep.db import api_keys

app = typer.Typer(help="Manage api keys.")


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
            help="The name of the api key.",
        ),
    ] = None,
    valid_until: Annotated[
        int,
        typer.Option(
            "--valid-until",
            "-v",
            help="The unix timestamp when the api key expires. Defaults to -1 which means that the key never expires.",
        ),
    ] = -1,
    credits: Annotated[
        int,
        typer.Option(
            "--credits",
            "-c",
            help="The number of credits the api key has. -1 means unlimited.",
        ),
    ] = -1,
    enabled: Annotated[
        bool,
        typer.Option(
            "--enabled",
            "-e",
            help="Whether the api key is enabled. Disabled keys cannot make requests.",
        ),
    ] = True,
):
    """
    Create a new api key.
    """
    api_key = api_keys.insert(
        name=name, valid_until=valid_until, credits=credits, enabled=enabled
    )
    print(api_key)


@app.command()
def list():
    """
    List all api keys.
    """
    all = api_keys.get_all()
    print(api_keys.ApiKey.tabulate(all))


@app.command()
def delete(
    query: Annotated[
        str,
        typer.Argument(
            help="The api key to delete. Can be specified by either the key or its numerical id.",
        ),
    ]
):
    """
    Deletes an api key.
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
            help="The api key to edit. Can be specified by either the key or its numerical id.",
        ),
    ],
    # Values as options
    api_key_hint: str = typer.Option(None, "--api_key_hint", "-k"),
    name: str = typer.Option(None, "--name", "-n"),
    request_count: int = typer.Option(None, "--request_count", "-r"),
    valid_until: int = typer.Option(None, "--valid_until", "-u"),
    credits: int = typer.Option(None, "--credits", "-c"),
    enabled: bool = typer.Option(None, "--enabled", "-e"),
):
    """
    Edit an api key.
    """
    api_keys.update(
        query,
        api_key_hint,
        name,
        request_count,
        valid_until,
        credits,
        enabled,
    )
    print(api_keys.get(query))
