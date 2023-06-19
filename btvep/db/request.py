import datetime
import time
from peewee import *
from tabulate import tabulate

from btvep.db.api_keys import ApiKey

from .utils import db


class Request(Model):
    id = AutoField()
    api_key = ForeignKeyField(ApiKey, field="api_key", backref="requests")
    timestamp = IntegerField(default=int(time.time()))
    prompt = TextField()
    response = TextField()
    responder_hotkey = TextField()

    class Meta:
        database = db

    @staticmethod
    def tabulate(requests):
        """Print a list of requests in a table."""
        return tabulate(
            requests,
            headers="keys",
        )


db.create_tables([Request])
