from datetime import datetime
from typing import Annotated

import typer

from btvep.db.request import Request

app = typer.Typer(help="Inspect request logs.")


@app.callback(invoke_without_command=True)
def main(
    key: Annotated[
        str,
        typer.Option(
            "--key",
            "-k",
            help="Filter logs by API key.",
        ),
    ] = None,
    responder_hotkey: Annotated[
        str,
        typer.Option(
            "--responder-hotkey",
            "-r",
            help="Filter logs by responder hotkey.",
        ),
    ] = None,
    lines: Annotated[
        int,
        typer.Option(
            "--lines",
            "-l",
            help="Maximum number of lines to print.",
        ),
    ] = 100,
    start: Annotated[
        datetime,
        typer.Option(
            "--start",
            "-s",
            help="The start of the time range to inspect.",
        ),
    ] = None,
    end: Annotated[
        datetime,
        typer.Option(
            "--end",
            "-e",
            help="The end of the time range to inspect.",
        ),
    ] = None,
):
    """
    Inspect request logs.
    """
    # Create the base query
    log_entries_query = Request.select().order_by(Request.timestamp.desc()).limit(lines)

    # Append conditions if the respective parameters are provided
    if key is not None:
        log_entries_query = log_entries_query.where(Request.api_key_id == key)
    if start is not None and end is not None:
        log_entries_query = log_entries_query.where(
            Request.timestamp.between(start, end)
        )
    elif start is not None:
        log_entries_query = log_entries_query.where(Request.timestamp >= start)
    elif end is not None:
        log_entries_query = log_entries_query.where(Request.timestamp <= end)
    elif responder_hotkey is not None:
        log_entries_query = log_entries_query.where(
            Request.responder_hotkey == responder_hotkey
        )

    log_entries = [log for log in log_entries_query.dicts().iterator()]
    print(Request.tabulate(log_entries))
