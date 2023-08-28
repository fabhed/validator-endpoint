from contextvars import ContextVar
import os
import peewee

DB_PATH = os.path.join(os.path.dirname(__file__), "../../btvep.db")
DB_PATH = os.path.abspath(DB_PATH)

# https://fastapi.tiangolo.com/advanced/sql-databases-peewee/#make-peewee-async-compatible-peeweeconnectionstate
db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = peewee.SqliteDatabase(DB_PATH, check_same_thread=False)
db._state = PeeweeConnectionState()


class BaseModel(peewee.Model):
    class Meta:
        database = db
