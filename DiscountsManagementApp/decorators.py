from functools import wraps

from flask import redirect, url_for
from flask_login import login_required, current_user


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
