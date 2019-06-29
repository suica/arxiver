from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import SECRET_KEY
from flask import request, abort, g
from functools import wraps
from models import User

token_serializer = Serializer(SECRET_KEY, expires_in=3600)
auth = HTTPTokenAuth('Bearer')


@auth.verify_token
def verify_token(token):
    g.user = None
    g.ip = 'unknown'
    try:
        data = token_serializer.loads(token)
    except:
        return False
    if 'id' in data:
        g.user = data['id']
        g.role = User.get_by_primary_key(g.user).role_id
        g.ip = request.remote_addr
        return True
    return False


def permission_required(permissons):
    def inner(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if g.user:
                g.role = User.get_by_primary_key(g.user).role_id
                if g.role in permissons:
                    return f(*args, **kwargs)
            abort(403)

        return decorator

    return inner


def assert_permission(roles, user_id=None):
    if g.user:
        if g.role in roles or user_id == g.user:
            return
    if len(roles) == 0:
        return
    abort(403)


def check_permission(roles, user_id=None):
    if g.user:
        if g.role in roles or user_id == g.user:
            return True
    if len(roles) == 0:
        return True
    return False
