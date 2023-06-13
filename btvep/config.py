import os
import json
from typing import List
from rich.console import Console
import typer

from btvep.btvep_models import RateLimit

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)

from pydantic import BaseModel


def cast_str_to_bool(value: str) -> bool:
    if value.lower() in ["true", "1"]:
        return True
    elif value.lower() in ["false", "0"]:
        return False
    else:
        raise ValueError(f"Invalid value for bool: {value}")


class Config(BaseModel):
    hotkey_mnemonic: str | None = None
    rate_limiting_enabled = False
    redis_url = "redis://localhost"
    global_rate_limits: List[RateLimit] = []

    source_info = {}

    def to_json(self, hide_mnemonic=False, include_source_info=False):
        obj_as_dict = self.dict()
        obj_as_dict.pop("source_info")

        if hide_mnemonic:
            obj_as_dict["hotkey_mnemonic"] = "********"

        if include_source_info:
            for key in self.source_info:
                obj_as_dict[key] += f" (from {self.source_info[key]})"

        return json.dumps(
            obj_as_dict, default=lambda o: o.dict(), sort_keys=False, indent=4
        )

    def save(self):
        #  save to a json file
        with open(CONFIG_PATH, "w") as jsonfile:
            jsonfile.write(self.to_json())
        return self

    def load(self):
        # load from json file
        self.load_json()
        # load from environment variables
        self.load_env()
        return self

    def load_json(self):
        # load from a json file and handle error silently
        try:
            with open(CONFIG_PATH, "r") as jsonfile:
                json_data = json.load(jsonfile)
                self.__dict__.update(json_data)
            return self
        except FileNotFoundError as e:
            return self
        except json.JSONDecodeError as e:
            err_console = Console(stderr=True)
            err_console.print(
                f"[bold red]Error:[/bold red] {CONFIG_PATH} is not a valid json file. Please fix it or delete it and try again."
            )
            raise typer.Exit(1)

    def load_env(self):
        # load from environment variables
        if "HOTKEY_MNEMONIC" in os.environ:
            self.hotkey_mnemonic = os.getenv("HOTKEY_MNEMONIC")
            self.source_info["hotkey_mnemonic"] = "environment variable"

        if "RATE_LIMITING_ENABLED" in os.environ:
            self.rate_limiting_enabled = cast_str_to_bool(
                os.getenv("RATE_LIMITING_ENABLED")
            )
            self.source_info["rate_limiting_enabled"] = "environment variable"

        if "REDIS_URL" in os.environ:
            self.redis_url = os.getenv("REDIS_URL")
            self.source_info["redis_url"] = "environment variable"

        if "GLOBAL_RATE_LIMITS" in os.environ:
            self.global_rate_limits = json.loads(os.getenv("GLOBAL_RATE_LIMITS"))
            self.source_info["global_rate_limits"] = "environment variable"

        return self

    def validate(self):
        # validate mnemonic
        if self.hotkey_mnemonic is None:
            typer.echo(
                "[red]Missing hotkey mnemonic. Set the HOTKEY_MNEMONIC environment variable or set it with: btvep config set hotkey_mnemonic <mnemonic>[/red]"
            )
            raise typer.Exit(1)
        hotkey_mnemonic = hotkey_mnemonic.split()
        allowed_word_counts = [12, 15, 18, 21, 24]
        if len(hotkey_mnemonic) not in allowed_word_counts:
            typer.echo(
                f"[red]hotkey_mnemonic has an invalid size. It should be 12, 15, 18, 21 or 24 words[/red]"
            )
            raise typer.Exit(1)
        return self

    # Print format
    def __str__(self):
        # use __dict__
        return self.to_json()
