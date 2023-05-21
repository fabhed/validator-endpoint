"""This module provides the CLI"""

from typing import Optional

import typer

from vendpoint import __app_name__, __version__

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def _start_callback():
    import uvicorn

    uvicorn.run("vendpoint.server:app", host="0.0.0.0", port=8000)


@app.callback()
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
    return


@app.command()
def start():
    print("Starting the api server...")
    _start_callback()
