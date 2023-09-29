import json
import time

from peewee import BooleanField, DateTimeField, IntegerField, TextField
from tabulate import tabulate

from .utils import BaseModel, db


class User(BaseModel):
    id = TextField(primary_key=True)
    # Number of requests to the bittensor network
    request_count = IntegerField(default=0)
    is_admin = IntegerField(default=0)
    # Number of requests to the validator-endpoint api (one api request can make multiple bittensor requests)
    api_request_count = IntegerField(default=0)
    enabled = BooleanField(default=True)
    created_at = DateTimeField(default=lambda: int(time.time()))
    updated_at = DateTimeField(default=lambda: int(time.time()))


    def __str__(self):
        return json.dumps(self.__dict__["__data__"], indent=4, default=str)

    @staticmethod
    def tabulate(users):
        """Print a list of API keys in a table."""
        return tabulate(
            users,
            headers="users",
        )


db.create_tables([User])
