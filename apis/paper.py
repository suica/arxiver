from flask import g
from flask_restful import Resource

from models import db, User, Paper, Tag
from utils.api_utils import *
from utils.auth_utils import auth, assert_permission
from utils.log_utils import log_and_capture

UserHasPaper = User.UserHasPaper
PaperHasTag = Paper.PaperHasTag


class PaperAPI(Resource):

    def get(self, paper_id=''):
        if paper_id == 'random':
            from sqlalchemy.sql.functions import random
            result = Paper.query.order_by(random()).first()
        else:
            result = Paper.query.filter_by(id=paper_id).first()
        if result:
            return result
        else:
            return error('Paper not found'), 400


class PaperListAPI(Resource):

    # @fields({'_tags': str, '_finished': str, '_keyword': str, '_keyword_column': str})
    # def orz(self, user_id, page=1, per_page=20, tags='', finished='', keyword='', keyword_column=''):
    #     print(tags, finished, per_page, keyword, keyword_column)
    #     if user_id == 0:
    #         user_id = g.user
    #     check_permission([MASTER, GRANDMASTER], user_id=user_id)

    @pagination()
    @fields({'_tags': str, '_keyword': str, '_keyword_column': str})
    def get(self, page=1, per_page=20, tags='', keyword='', keyword_column=''):
        page = max(page, 1)
        tags = to_str_list(tags)
        # print('papers get', page, per_page, tags, keyword, keyword_column)

        q = Paper.query
        if len(tags):
            q = q.join(PaperHasTag).filter(PaperHasTag.tag_name.in_(tags))
        if len(keyword) and len(keyword_column):
            if keyword_column in Paper._dict_fields:
                attr = getattr(Paper, keyword_column)
                q = q.filter(attr.like('%{}%'.format(keyword)))
        pagi = q.order_by(db.desc(Paper.published)).paginate(page=page, per_page=per_page)
        dic = make_pagnination_info_dict(pagi)
        return dic


class PaperSubcriptionAPI(Resource):
    decorators = [auth.login_required]

    @log_and_capture('delete paper error')
    def delete(self, user_id, paper_id):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)
        has_paper = User.UserHasPaper.query.filter_by(user_id=user_id, paper_id=paper_id).first()
        db.session.delete(has_paper)
        db.session.commit()
        return error('delete ok'), 200

    @log_and_capture('paper subscription put error')
    @fields({'finished': int})
    def put(self, user_id, paper_id, finished=False):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)
        has_papers = User.UserHasPaper.query.filter_by(user_id=user_id, paper_id=paper_id).first()
        has_papers.finished = finished
        db.session.commit()
        return has_papers

    @log_and_capture('paper subscription get error')
    @fields({'_tags': str, '_finished': str, })
    def get(self, user_id, paper_id, tags='', finished=''):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)
        has_paper = User.UserHasPaper.query.filter_by(user_id=user_id, paper_id=paper_id).first()
        return has_paper


class PaperSubscriptionQueueAPI(Resource):
    decorators = [auth.login_required]

    @log_and_capture()
    def post(self, user_id, paper_id_1, method, position):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)

        supported_method = ['insert_at_position']

        if method not in supported_method:
            raise NotImplementedError('no method={}'.format(method))

        paper1 = User.UserHasPaper.query.filter_by(paper_id=paper_id_1, user_id=user_id).first()
        user = User.query.filter_by(id=user_id).first()
        user.paper_queue.remove(paper1)
        user.paper_queue.insert(position, paper1)
        db.session.commit()
        return error('ok'), 200


def to_bool(s):
    re = []
    if '1' in s:
        re += [True]
    if '0' in s:
        re += [False]
    return re


def to_str_list(s):
    if len(s):
        return s.split(',')
    return []


def to_wild_card(s):
    s = s.replace(',', ' ')
    re = s.split(' ')
    return re


class PaperSubcriptionListAPI(Resource):
    decorators = [auth.login_required]

    @log_and_capture()
    @pagination()
    @fields({'_tags': str, '_finished': str, '_keyword': str, '_keyword_column': str})
    def get(self, user_id, page=1, per_page=10, tags='', finished='', keyword='', keyword_column=''):
        if user_id == 0:
            user_id = g.user
        tags = to_str_list(tags)
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)
        q = UserHasPaper.query.filter_by(user_id=user_id).join(Paper, PaperHasTag)
        if len(tags):
            q = q.filter(PaperHasTag.tag_name.in_(tags))
        if len(finished):
            q = q.filter(UserHasPaper.finished.in_(finished))
        if len(keyword) and len(keyword_column):
            if keyword_column in Paper._dict_fields:
                attr = getattr(Paper, keyword_column)
                q = q.filter(attr.like('%{}%'.format(keyword)))

        pagi = q.order_by(db.asc(User.UserHasPaper.position)).paginate(page=page, per_page=per_page)
        dic = make_pagnination_info_dict(pagi)
        return dic

    @log_and_capture()
    @fields({'paper_id': str, '_create': bool})
    def post(self, user_id, paper_id=None, create=None):
        if user_id == 0:
            user_id = g.user
        assert_permission([MASTER, GRANDMASTER], user_id=user_id)

        if create:
            from async_tasks.fetch_paper import fetch
            worker = fetch.delay(paper_id)
            paper_data = worker.get(10)[0]
            if Paper.query.filter_by(id=Paper.url_to_id(paper_data['id'])).first() is None:
                paper = Paper(**paper_data)
                db.session.add(paper)
                db.session.commit()
                paper_id = paper.id
        has_paper = User.get_by_primary_key(user_id).add_paper(paper_id)
        if has_paper:
            return has_paper
        return error('Subscribe failed.'), 400


class TagListAPI(Resource):

    def get(self):
        return Tag.query.all()
