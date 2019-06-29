from flask import g
from flask_restful import Resource

from models import db, User
from utils.api_utils import *
from utils.auth_utils import auth, assert_permission, check_permission
from utils.log_utils import log_and_capture
from utils.validation_utils import validate_password, validate_username


class UserAPI(Resource):
    decorators = [auth.login_required]

    @log_and_capture()
    def get(self, id):
        if id == 0:
            id = g.user
        x = User.query.filter_by(id=id).first()
        if x:
            return x
        else:
            error('No user with id={}.'.format(id)), 400

    @log_and_capture()
    @fields({'_role_id': int, '_email': str, '_username': str})
    def put(self, id, role_id=None, email=None, username=None):
        user = User.query.filter_by(id=id).first()
        assert_permission([MASTER, GRANDMASTER], user_id=g.user)
        for k in ['email']:
            if locals()[k] is not None:
                user.__setattr__(k, locals()[k])
        if check_permission([GRANDMASTER]):
            for k in ['username', 'role_id']:
                if locals()[k] is not None:
                    user.role_id = role_id
        db.session.commit()
        return user


class UserListAPI(Resource):

    @fields({'username': str, 'password': str})
    def post(self, username=None, password=None):
        cnt = User.query.filter_by(username=username).count()
        if cnt > 0:
            return error('This name has already been used.'), 400
        if not validate_username(username):
            return error('This name is not validated.'), 400
        if not validate_password(password):
            return error('This password is not validated.'), 400
        new_user = User(username, password, READER)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @log_and_capture()
    @pagination()
    @auth.login_required
    def get(self, page=1, per_page=10):
        assert_permission([MASTER, GRANDMASTER])
        pagi = User.query.paginate(page=page, per_page=per_page)
        dic = make_pagnination_info_dict(pagi)
        return dic


class PasswordAPI(Resource):
    decorators = [auth.login_required]

    @log_and_capture()
    @fields({'old_pwd': str, 'new_pwd': str})
    def put(self, user_id, old_pwd=None, new_pwd=None):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)
        user = User.query.filter_by(id=user_id).first()
        if user.verify_password(old_pwd):
            if validate_password(new_pwd):
                if old_pwd == new_pwd:
                    return error('New password cannot be identical to the old one.'), 400
                user.password = user.hash_password(new_pwd)
                db.session.commit()
                return error('Password updated.'), 200
            else:
                return error('New password is not validated.'), 400
        return error('Old password is not correct.'), 400
