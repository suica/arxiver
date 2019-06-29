from flask_restful import Resource
from utils.auth_utils import auth, permission_required
from models import Log, db
from utils.api_utils import *


class LogAPI(Resource):
    decorators = [auth.login_required]

    @permission_required([MASTER, GRANDMASTER])
    def get(self, log_id):
        log = Log.query.filter_by(id=log_id).first()
        if log:
            return log
        else:
            return error('no log with id={}'.format(log_id)), 400


class LogListAPI(Resource):
    decorators = [auth.login_required]

    @permission_required([MASTER, GRANDMASTER])
    @pagination()
    def get(self, page=1, per_page=20):
        pagi = Log.query.order_by(db.desc(Log.id)).paginate(page=page, per_page=per_page)
        dic = make_pagnination_info_dict(pagi)
        return dic
