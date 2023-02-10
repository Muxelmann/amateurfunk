from flask import g, request, redirect, url_for
from functools import wraps

def registration_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.registered_user_id is None:
            return redirect(url_for('auth.index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function