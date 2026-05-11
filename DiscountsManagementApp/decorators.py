from functools import wraps

from flask import redirect, url_for, jsonify, request
from flask_login import login_required, current_user


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role.name not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Bạn không có quyền truy cập tài nguyên này'}), 403
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
