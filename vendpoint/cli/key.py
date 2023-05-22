from typing import Annotated
import typer

from vendpoint.db import api_keys


def convert_to_int_if_numeric(value: str) -> int | str:
    if value.isnumeric():
        return int(value)
    return value


app = typer.Typer()


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
    print(f"Deleting key {query}")
    api_keys.delete(query)


# edit
@app.command()
def edit(
    query: Annotated[
        str,
        typer.Argument(
            help="The api key to delete. Can be specified by either the key or its numerical id.",
        ),
    ],
    # Values as options
    api_key_hint: str = typer.Option(None, "--api-key-hint", "-k"),
    name: str = typer.Option(None, "--name", "-n"),
    request_count: int = typer.Option(None, "--request-count", "-r"),
    valid_until: int = typer.Option(None, "--valid-until", "-u"),
    credits: int = typer.Option(None, "--credits", "-c"),
    enabled: bool = typer.Option(None, "--enabled", "-e"),
):
    """
    Edit an api key.
    """
    api_key = api_keys.update(
        convert_to_int_if_numeric(query),
        api_key_hint,
        name,
        request_count,
        valid_until,
        credits,
        enabled,
    )

    print(api_key)
