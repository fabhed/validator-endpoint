from ast import List
import json
import secrets
import time

from peewee import (
    BooleanField,
    DateTimeField,
    DoesNotExist,
    IntegerField,
    TextField,
    ForeignKeyField,
)
from tabulate import tabulate
from btvep.btvep_models import RateLimitEntry
from btvep.db.user import User

from btvep.models.key import ApiKeyInDB

from .utils import BaseModel

KEY_LENGTH = 48


class ApiKey(BaseModel):
    id = IntegerField(primary_key=True)
    api_key = TextField(unique=True)
    api_key_hint = TextField()
    name = TextField(null=True)
    user = ForeignKeyField(User, field="id", backref="api_keys", null=True)
    # Number of requests to the bittensor network
    request_count = IntegerField(default=0)
    # Number of requests to the validator-endpoint api (one api request can make multiple bittensor requests)
    api_request_count = IntegerField(default=0)
    valid_until = DateTimeField(default=-1)
    credits = IntegerField(default=-1)
    enabled = BooleanField(default=True)
    rate_limits = TextField(null=True)
    rate_limits_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=lambda: int(time.time()))
    updated_at = DateTimeField(default=lambda: int(time.time()))

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
    api_key: str = None,
    user_id: str = None,
    request_count: int = 0,
    api_request_count: int = 0,
    valid_until: int = -1,
    credits: int = -1,
    enabled: bool = True,
    name: str = None,
) -> ApiKey:
    if api_key is None:
        api_key = secrets.token_urlsafe(KEY_LENGTH)

    return ApiKey.create(
        api_key=api_key,
        user_id=user_id,
        api_key_hint="..." + api_key[-4:],
        request_count=request_count,
        api_request_count=api_request_count,
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


def get_by_key(api_key: str) -> ApiKey:
    try:
        return ApiKey.get((ApiKey.api_key == api_key))
    except DoesNotExist as error:
        print(error)
        return None


def get_all() -> list[ApiKeyInDB]:
    return [key for key in ApiKey.select().dicts().order_by(ApiKey.id.desc())]


def get_all_by_user_id(user_id: str) -> list[ApiKeyInDB]:
    return [
        key
        for key in ApiKey.select()
        .where((ApiKey.user == user_id))
        .dicts()
        .order_by(ApiKey.id.desc())
    ]


def update(
    #
    # Query fields
    #
    query: str | int,
    # user_id is Additional to query, to prevent users from editing other users' keys
    user_id: str = None,
    #
    # Update fields
    #
    api_key_hint: str = None,
    name: str = None,
    request_count: int = None,
    api_request_count: int = None,
    valid_until: int = None,
    credits: int = None,
    enabled: bool = None,
    rate_limits: str = None,
    rate_limits_enabled: bool = None,
):
    # Use a dict to filter out None values
    update_dict = {
        "api_key_hint": api_key_hint,
        "name": name,
        "request_count": request_count,
        "api_request_count": api_request_count,
        "valid_until": valid_until,
        "credits": credits,
        "enabled": enabled,
        "updated_at": int(time.time()),
        "rate_limits": json.dumps([rate_limit.dict() for rate_limit in rate_limits])
        if rate_limits
        else None,
        "rate_limits_enabled": rate_limits_enabled,
    }
    update_dict = {k: v for k, v in update_dict.items() if v is not None}

    q = ApiKey.update(update_dict)
    criteria = (ApiKey.id == query) | (ApiKey.api_key == query)

    # Add user_id to criteria if it is provided
    if user_id is not None:
        criteria &= ApiKey.user_id == user_id

    return q.where(criteria).execute()


def delete(id_or_key: str | int, user_id: str = None):
    """
    Delete an API key.
    """

    # Start the query
    q = ApiKey.delete()

    # Base criteria
    criteria = (ApiKey.id == id_or_key) | (ApiKey.api_key == id_or_key)

    # Add user_id to criteria if it is provided
    if user_id is not None:
        criteria &= ApiKey.user_id == user_id

    return q.where(criteria).execute()
