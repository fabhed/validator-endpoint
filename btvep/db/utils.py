import os
from peewee import SqliteDatabase, Model

DB_PATH = os.path.join(os.path.dirname(__file__), "../../btvep.db")
DB_PATH = os.path.abspath(DB_PATH)
db = SqliteDatabase(DB_PATH, check_same_thread=False)


class BaseModel(Model):
    class Meta:
        database = db
