import logging
import traceback
from functools import wraps

from flask import g, request

from utils.api_utils import error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app')


def get_log(func, msg='', trace=''):
    # api_name, method = func.__qualname__.split('.')
    k = func.__qualname__.split('.')
    api_name, method = k

    if 'role' in g:
        role = g.role
    else:
        role = -1
    if 'user' in g:
        user = g.user
    else:
        user = -1
    level = 1
    if len(trace):
        level = 3
    if method == 'delete':
        level = 2
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    return {
        'ip':ip,
        'user_id': user,
        'method': method,
        'api_name': api_name,
        'role_id': role,
        'trace': trace,
        'message': msg,
        'level': level,
    }


def log_and_capture(user_log=True, msg='error', code=400):
    def inner(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            log_obj = None
            result = None
            try:
                result = f(*args, **kwargs)
                log_obj = get_log(f)
            except Exception as e:
                result = error(msg), code
                trace = traceback.format_exc()
                logger.warning(trace)
                log_obj = get_log(f, msg=str(e), trace=trace)
            newlog = Log(**log_obj)
            db.session.add(newlog)
            db.session.commit()
            return result

        return decorator

    return inner


from models import db, Log
