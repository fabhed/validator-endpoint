from .utils import db
from .api_keys import ApiKey


def create_all():
    db.create_tables([ApiKey])
