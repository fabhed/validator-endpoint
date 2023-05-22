"""This module provides the CLI"""

from typing import Optional

import typer
from typing_extensions import Annotated

from btvep import __app_name__, __version__, db

from . import key
from . import config

app = typer.Typer(help="Bitensor Validator Endpoint CLI")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback(no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """btvep entry point"""
    db.tables.create_all()
    return


@app.command()
def start(
    port: Annotated[
        int,
        typer.Option(
            help="The port to listen on.",
        ),
    ] = 8000,
):
    """
    Start the api server.
    """
    import uvicorn

    uvicorn.run("btvep.server:app", host="0.0.0.0", port=port)


app.add_typer(key.app, name="key")
app.add_typer(config.app, name="config")
