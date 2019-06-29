from functools import wraps

from flask_restful import reqparse

GRANDMASTER = 3
MASTER = 2
READER = 1


def error(msg):
    return {
        'error_msg': msg
    }


def fields(dic):
    def inner(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            parser = reqparse.RequestParser()
            for k, v in dic.items():
                if k.startswith('_'):
                    parser.add_argument(k[1:], type=v, help='{} error'.format(k))
                else:
                    parser.add_argument(k, type=v, help='{} error'.format(k), required=True)
            parsed_args = parser.parse_args()
            for k, v in parsed_args.items():
                if v is not None:
                    kwargs[k] = v
            return f(*args, **kwargs)

        return decorator

    return inner


def pagination():
    return fields({'_page': int, '_per_page': int})


def make_pagnination_info_dict(pagination_obj):
    page = pagination_obj.page
    per_page = pagination_obj.per_page
    # if pagination_obj.has_prev:
    #     prev_url = container.url_for(resource, page=page - 1, per_page=per_page)
    # if pagination_obj.has_next:
    #     next_url = container.url_for(resource, page=page + 1, per_page=per_page)
    dic = {
        "page": page,
        "total_pages": pagination_obj.pages,
        "per_page": per_page,
        "has_next": pagination_obj.has_next,
        "has_prev": pagination_obj.has_prev,
        "total_items": pagination_obj.total,
        'items': pagination_obj.items
    }
    return dic
