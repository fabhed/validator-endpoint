import datetime
from peewee import *

from btvep.db.api_keys import ApiKey

from .utils import db


class Request(Model):
    id = AutoField()
    api_key = ForeignKeyField(ApiKey, field="api_key")
    timestamp = TimestampField(default=datetime.datetime.now)
    prompt = TextField()
    response = TextField()

    class Meta:
        database = db


db.create_tables([Request])
