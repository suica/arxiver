from flask_restful import Resource
from flask import after_this_request

from models import User
from utils.api_utils import *
from utils.log_utils import log_and_capture


class AuthAPI(Resource):

    @log_and_capture()
    @fields({'username': str, 'password': str})
    def post(self, username=None, password=None):

        user = User.query.filter_by(username=username).first()
        if user:
            if user.verify_password(password):
                token = user.generate_auth_token()

                @after_this_request
                def set_cookie(response):
                    response.set_cookie('logged_in_as', str(user.role_id), max_age=64800)
                    return response

                return {
                    'token': token.decode('ascii')
                }

        return error('password or username error'), 400
