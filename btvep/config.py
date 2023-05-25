import os
import json
from rich.console import Console
import typer

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)


class Config:
    def __init__(self):
        self.hotkey_mnemonic = None

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def save(self):
        #  save to a json file
        with open(CONFIG_PATH, "w") as jsonfile:
            jsonfile.write(self.to_json())
        return self

    def load(self):
        # load from a json file and handle error silently
        try:
            with open(CONFIG_PATH, "r") as jsonfile:
                json_data = json.load(jsonfile)
                self.hotkey_mnemonic = json_data["hotkey_mnemonic"]
            return self
        except FileNotFoundError as e:
            return self
        except json.JSONDecodeError as e:
            err_console = Console(stderr=True)
            err_console.print(
                f"[bold red]Error:[/bold red] {CONFIG_PATH} is not a valid json file. Please fix it or delete it and try again."
            )
            raise typer.Exit(1)

    # Print format
    def __str__(self):
        # use __dict__
        return str(self.__dict__)
