import sqlite3
from sqlite3 import Error

connection = None


def create_or_get_connection() -> sqlite3.Connection:
    global connection
    if connection is not None:
        return connection
    try:
        connection = sqlite3.connect("btvep.db", check_same_thread=False)
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
