import typer

from vendpoint.db import api_keys

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main():
    pass


@app.command()
def create():
    """
    Create a new api key.
    """
    api_key = api_keys.insert()
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
    api_key: str,
):
    """
    Delete an api key.
    """
    print(f"Deleting key {api_key}")
    api_keys.delete(api_key)


# edit
@app.command()
def edit(
    api_key: str,
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
        api_key,
        api_key_hint,
        name,
        request_count,
        valid_until,
        credits,
        enabled,
    )

    print(api_key)
