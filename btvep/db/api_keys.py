from tabulate import tabulate
from .utils import create_or_get_connection


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


def get_column_to_query(query):
    return "id" if isinstance(query, int) else "api_key"


class ApiKey:
    # Init method taking db output
    def __init__(self, db_output):
        self.id = db_output[0]
        self.api_key = db_output[1]
        self.api_key_hint = db_output[2]
        self.name = db_output[3]
        self.request_count = db_output[4]
        self.valid_until = db_output[5]
        self.credits = db_output[6]
        self.enabled = db_output[7]
        self.created_at = db_output[8]
        self.updated_at = db_output[9]

    def has_unlimited_credits(self):
        return self.credits == -1

    def has_lifetime(self):
        return self.valid_until != -1

    # Define print as a table
    def __str__(self):
        return tabulate(
            [self.__dict__.values()],
            headers=column_order,
        )

    # Define print as a table for lists of ApiKey objects static
    @staticmethod
    def tabulate(api_keys):
        return tabulate(
            [api_key.__dict__.values() for api_key in api_keys],
            headers=column_order,
        )


import secrets

KEY_LENGTH = 48


def create_table():
    connection = create_or_get_connection()
    with connection:
        cur = connection.cursor()
        # Api keys table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                api_key TEXT UNIQUE,
                api_key_hint TEXT,
                name TEXT,
                request_count INTEGER,
                valid_until INTEGER,
                credits INTEGER,
                enabled INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# Set defaults in params
def insert(
    api_key: str = secrets.token_urlsafe(KEY_LENGTH),
    request_count: int = 0,
    # Test
    valid_until: int = -1,
    credits: int = -1,
    enabled: bool = True,
    name: str = None,
):
    connection = create_or_get_connection()
    cur = connection.cursor()

    with connection:
        cur.execute(
            """
            INSERT INTO api_keys (api_key, api_key_hint, name, request_count, valid_until, credits, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                api_key,
                "..." + api_key[-4:],
                name,
                request_count,
                valid_until,
                credits,
                enabled,
            ),
        )
        return get(api_key)


def get(query: str | int) -> ApiKey:
    column_to_query = get_column_to_query(query)
    connection = create_or_get_connection()
    cur = connection.cursor()
    cur.execute(
        """
        SELECT * FROM api_keys WHERE {} = ?
        """.format(
            column_to_query
        ),
        (query,),
    )
    res = cur.fetchone()
    return None if res is None else ApiKey(res)


def get_all():
    connection = create_or_get_connection()
    cur = connection.cursor()
    cur.execute(
        """
        SELECT * FROM api_keys
        """
    )
    return [ApiKey(row) for row in cur.fetchall()]


# Update function
def update(
    query: str | int,
    api_key_hint: str = None,
    name: str = None,
    request_count: int = None,
    valid_until: int = None,
    credits: int = None,
    enabled: bool = None,
):
    """
    Update an api key with the given query.
    Args:
        query: The query to find the api key to update. Can be either the api key or the id.

    """
    column_to_query = get_column_to_query(query)

    connection = create_or_get_connection()
    cur = connection.cursor()
    with connection:
        cur.execute(
            """
            UPDATE api_keys
            SET api_key_hint = COALESCE(?, api_key_hint),
                name = COALESCE(?, name),
                request_count = COALESCE(?, request_count),
                valid_until = COALESCE(?, valid_until),
                credits = COALESCE(?, credits),
                enabled = COALESCE(?, enabled),
                updated_at = CURRENT_TIMESTAMP
            WHERE {} = ?
            """.format(
                column_to_query
            ),
            (
                api_key_hint,
                name,
                request_count,
                valid_until,
                credits,
                enabled,
                query,
            ),
        )
        return ApiKey(get(query))


# Delete function
def delete(api_key: str | int):
    column_to_query = get_column_to_query(api_key)
    connection = create_or_get_connection()
    cur = connection.cursor()
    with connection:
        cur.execute(
            """
            DELETE FROM api_keys
            WHERE {} = ?
            """.format(
                column_to_query
            ),
            (api_key,),
        )
