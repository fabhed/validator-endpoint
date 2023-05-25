import datetime
import json
from collections import OrderedDict

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

import secrets

KEY_LENGTH = 48


#################### Reimplment this file with peewee ####################
from peewee import BooleanField, DateTimeField, IntegerField, Model, TextField


class ApiKey(BaseModel):
    api_key = TextField(unique=True)
    api_key_hint = TextField()
    name = TextField(null=True)
    request_count = IntegerField(default=0)
    valid_until = DateTimeField(default=-1)
    credits = IntegerField(default=-1)
    enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def has_unlimited_credits(self):
        return self.credits == -1

    def has_lifetime(self):
        return self.valid_until != -1

    def __str__(self):
        # Print dict data with indents using json

        # sortedDict = OrderedDict(
        #     sorted(self.__dict__["__data__"], key=lambda x: column_order.index(x[0]))
        # )
        return json.dumps(self.__dict__["__data__"], indent=4, default=str)

    # Define print as a table for lists of ApiKey objects static
    @staticmethod
    def tabulate(api_keys):
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
    column_to_query = get_column_to_query(query)
    # Return none if does not exist
    try:
        return ApiKey.get(column_to_query == query)
    except ApiKey.DoesNotExist as e:
        print(e)
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
    api_key = get(query)
    if api_key_hint is not None:
        api_key.api_key_hint = api_key_hint
    if name is not None:
        api_key.name = name
    if request_count is not None:
        api_key.request_count = request_count
    if valid_until is not None:
        api_key.valid_until = valid_until
    if credits is not None:
        api_key.credits = credits
    if enabled is not None:
        api_key.enabled = enabled
    api_key.save()
    return api_key


def delete(api_key: str | int):
    api_key = get(api_key)
    return api_key.delete_instance()


def get_column_to_query(query: str | int):
    if isinstance(query, str):
        return ApiKey.api_key
    elif isinstance(query, int):
        return ApiKey.id
    else:
        raise ValueError("Query must be either a string or an integer")
