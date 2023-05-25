from . import api_keys, utils, tables

import os
from peewee import SqliteDatabase

DB_PATH = os.path.join(os.path.dirname(__file__), "../../btvep.db")
DB_PATH = os.path.abspath(DB_PATH)
db = SqliteDatabase(DB_PATH)
