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

    # API fields - before request is sent to the bittensor network
    is_api_success = BooleanField()
    api_error = TextField(null=True)

    # Fields from DendriteCall class
    response = TextField(null=True)
    responder_hotkey = TextField(null=True)
    is_success = BooleanField(null=True)
    return_message = TextField(null=True)
    elapsed_time = FloatField(null=True)
    src_hotkey = TextField(null=True)
    src_version = IntegerField(null=True)
    dest_version = IntegerField(null=True)
    return_code = IntegerField(null=True)

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
