import json
import secrets
from datetime import datetime
from peewee import BooleanField, DateTimeField, IntegerField, TextField, DoesNotExist
from tabulate import tabulate
from .utils import BaseModel

column_order = (
    "id",
    "api_key",
    "api_key_hint",
    "name",
    "request_count",
    "valid_until",
    "credits",
    "enabled",
    "created_at",
    "updated_at",
)


KEY_LENGTH = 48


class ApiKey(BaseModel):
    id = IntegerField(primary_key=True)
    api_key = TextField(unique=True)
    api_key_hint = TextField()
    name = TextField(null=True)
    request_count = IntegerField(default=0)
    valid_until = DateTimeField(default=-1)
    credits = IntegerField(default=-1)
    enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def has_unlimited_credits(self):
        return self.credits == -1

    def has_lifetime(self):
        return self.valid_until != -1

    def __str__(self):
        return json.dumps(self.__dict__["__data__"], indent=4, default=str)

    @staticmethod
    def tabulate(api_keys):
        """Print a list of API keys in a table."""
        return tabulate(
            api_keys,
            headers="keys",
        )


def insert(
    api_key: str = secrets.token_urlsafe(KEY_LENGTH),
    request_count: int = 0,
    valid_until: int = -1,
    credits: int = -1,
    enabled: bool = True,
    name: str = None,
):
    return ApiKey.create(
        api_key=api_key,
        api_key_hint="..." + api_key[-4:],
        request_count=request_count,
        valid_until=valid_until,
        credits=credits,
        enabled=enabled,
        name=name,
    )


def get(query: str | int) -> ApiKey:
    try:
        return ApiKey.get((ApiKey.id == query) | (ApiKey.api_key == query))
    except DoesNotExist as error:
        print(error)
        return None


def get_all():
    return [key for key in ApiKey.select().dicts()]


def update(
    query: str | int,
    api_key_hint: str = None,
    name: str = None,
    request_count: int = None,
    valid_until: int = None,
    credits: int = None,
    enabled: bool = None,
):
    # Use a dict to filter out None values
    update_dict = {
        "api_key_hint": api_key_hint,
        "name": name,
        "request_count": request_count,
        "valid_until": valid_until,
        "credits": credits,
        "enabled": enabled,
        "updated_at": datetime.now(),
    }
    update_dict = {k: v for k, v in update_dict.items() if v is not None}
    q = ApiKey.update(update_dict).where(
        (ApiKey.id == query) | (ApiKey.api_key == query)
    )
    return q.execute()


def delete(query: str | int):
    return (
        ApiKey.delete()
        .where((ApiKey.id == query) | (ApiKey.api_key == query))
        .execute()
    )
