from functools import wraps
from app.models.base import db

def db_connect_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not db.connection().open:
            db.connect()
        return func(*args, **kwargs)
    return decorated_function