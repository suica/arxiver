from flask_restful import Resource
from utils.auth_utils import auth, permission_required
from models.database import Role
from utils.api_utils import *


class RoleListAPI(Resource):
    decorators = [auth.login_required]

    @permission_required([MASTER, GRANDMASTER])
    def get(self):
        x = Role.query.all()
        return x
