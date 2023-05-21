"""This module provides the CLI"""

from typing import Optional

import typer
from typing_extensions import Annotated

from vendpoint import __app_name__, __version__, db

from . import key

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
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
    """vendpoint entry point"""
    db.tables.create_all()
    return


@app.command()
def start():
    print("Starting the api server...")
    import uvicorn

    uvicorn.run("vendpoint.server:app", host="0.0.0.0", port=8000)


app.add_typer(key.app, name="key", help="Manage api keys.")
