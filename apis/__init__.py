from flask_restful import Api

api_prefix = '/api/v1'

restful = None


def init_api(app):
    global restful
    restful = Api(app)
    for res in resources:
        restful.add_resource(*res, endpoint=res[0].__name__)


from .user import UserAPI, UserListAPI, PasswordAPI
from .auth import AuthAPI
from .log import LogAPI, LogListAPI
from .paper import PaperAPI, PaperListAPI, PaperSubcriptionAPI, PaperSubcriptionListAPI, PaperSubscriptionQueueAPI, \
    TagListAPI

resources = [
    [UserAPI, api_prefix + '/users/<int:id>'],
    [UserListAPI, api_prefix + '/users'],
    [AuthAPI, api_prefix + '/auth'],
    [PaperListAPI, api_prefix + '/papers'],
    [PaperAPI, api_prefix + '/papers/<string:paper_id>'],
    [PaperSubcriptionListAPI, api_prefix + '/users/<int:user_id>/papers'],
    [PaperSubcriptionAPI, api_prefix + '/users/<int:user_id>/papers/<string:paper_id>'],
    [PaperSubscriptionQueueAPI,
     api_prefix + '/users/<int:user_id>/papers/<string:paper_id_1>/<string:method>/<int:position>'],
    [LogListAPI, api_prefix + '/logs'],
    [LogAPI, api_prefix + '/logs/<int:log_id>'],
    [TagListAPI, api_prefix + '/tags'],
    [PasswordAPI, api_prefix + '/users/<int:user_id>/password']
]
