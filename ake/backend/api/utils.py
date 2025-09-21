from functools import wraps
from flask import session
from core import create_response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return create_response(False, message="Unauthorized"), 401
        return f(*args, **kwargs)

    return decorated_function
