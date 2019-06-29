import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context
from sqlalchemy import Table, Column, Text, Integer, ForeignKey, Sequence, String, DateTime
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from config import SECRET_KEY
from utils.json_hack import Serializable

db = SQLAlchemy()
db.create_all()


def now():
    return datetime.datetime.now()


class Role(Serializable, db.Model):
    __tablename__ = 'role'

    id = Column(Integer, Sequence('role_id'), primary_key=True)
    name = Column(Text)

    _dict_fields = ['id', 'name']

    def __init__(self, role_name):
        self.name = role_name


class User(Serializable, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id'), primary_key=True)

    role = relationship("Role", backref='users_of_role')
    role_id = Column(Integer, ForeignKey('role.id'))

    username = Column(Text)
    password = Column(Text)
    email = Column(Text)

    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, onupdate=now)

    paper_queue = relationship("UserHasPaper", order_by="UserHasPaper.position",
                               collection_class=ordering_list('position'), )
    # papers = relationship('UserHasPaper', backref='users_of_paper',lazy='dynamic')

    _dict_fields = ['id', 'role_id', 'username', 'email']

    def __init__(self, username, password, role_id, email=''):
        self.username = username
        self.password = self.hash_password(password)
        self.role_id = role_id
        self.email = email

    def hash_password(self, password):
        return custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expiration=36000):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id, 'role_id': self.role_id})

    @staticmethod
    def get_by_primary_key(id):
        user = User.query.filter_by(id=id).first()
        if user:
            return user
        else:
            raise Exception

    def add_paper(self, paper_id):
        paper = Paper.query.filter_by(id=paper_id).first()
        if paper:
            has_paper = self.UserHasPaper.query.filter_by(paper_id=paper_id).first()
            if has_paper is None:
                has_paper = self.UserHasPaper()
                has_paper.paper = paper
            else:
                has_paper.finished = False
            self.paper_queue.append(has_paper)
            db.session.commit()
            return has_paper
        return False

    class UserHasPaper(Serializable, db.Model):
        __tablename__ = 'userhaspaper'
        paper_id = Column(String(128), ForeignKey('paper.id'), primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
        finished = Column(db.Boolean, default=False)
        created_at = Column(DateTime, default=now)
        paper = relationship("Paper")
        position = Column(Integer)
        created_at = Column(DateTime, default=now)

        _dict_fields = ['paper', 'finished', 'created_at', 'position']


authors_papers = Table('authors_papers', db.metadata,
                       Column('author_name', Integer, ForeignKey('author.name')),
                       Column('paper_id', String(128), ForeignKey('paper.id'))
                       )


class Tag(Serializable, db.Model):
    __tablename__ = 'tag'
    name = Column(String(128), primary_key=True)
    _dict_fields = ['name']


class Author(Serializable, db.Model):
    __tablename__ = 'author'
    name = Column(String(128), primary_key=True)
    _dict_fields = ['name']


class Paper(Serializable, db.Model):
    __tablename__ = 'paper'
    id = Column(String(128), primary_key=True)
    updated = Column(DateTime)
    published = Column(DateTime)
    title = Column(Text)
    summary = Column(Text)

    doi = Column(String(128))
    pdf_url = Column(Text)
    arxiv_comment = Column(Text)
    journal_reference = Column(Text)
    affiliation = Column(Text)

    authors = relationship('Author', secondary=authors_papers,
                           backref=db.backref('papers_of_author', lazy='dynamic'), lazy='dynamic')
    tags = relationship('PaperHasTag', backref='papers_of_tag', lazy='dynamic')

    _dict_fields = ['id', 'updated', 'published', 'title', 'summary', 'tags', 'authors', 'arxiv_comment',
                    'journal_reference', 'doi']

    def __init__(self, **kwargs):
        self.id = self.url_to_id(kwargs['id'])
        self.title = kwargs['title']
        self.summary = kwargs['summary']
        self.updated = datetime.datetime(*(kwargs['updated_parsed'][:6]))
        self.published = datetime.datetime(*(kwargs['published_parsed'][:6]))
        self.pdf_url = kwargs['pdf_url']
        self.affiliation = kwargs['affiliation']
        self.journal_reference = kwargs['journal_reference']
        self.doi = kwargs['doi']
        self.arxiv_comment = kwargs['arxiv_comment']

        if 'authors' in kwargs:
            for author in kwargs['authors']:
                self.add_author(author)
        if 'tags' in kwargs:
            for tag_dict in kwargs['tags']:
                is_primary = False
                tag_name = tag_dict['term']
                try:
                    if tag_name == kwargs['arxiv_primary_category']['term']:
                        is_primary = True
                except:
                    pass
                self.add_tag(tag_name, is_primary)

    @staticmethod
    def url_to_id(url):
        id = url.replace('http://arxiv.org/abs/', '')
        id = id.replace('https://arxiv.org/abs/', '')
        id = id.replace('/', ':')
        return id

    @staticmethod
    def id_to_url(paper_id, prefix='http://arxiv.org/abs/'):
        url = prefix + paper_id.replace(':', '/')
        return url

    def add_author(self, author_name):
        au = Author.query.filter_by(name=author_name).first()
        if au:
            self.authors.append(au)
        else:
            self.authors.append(Author(name=author_name))
        return True

    def add_tag(self, tag_name, is_primary):
        relation = self.PaperHasTag(is_primary=is_primary)
        relation.tag = Tag.query.filter_by(name=tag_name).first()
        if not relation.tag:
            relation.tag = Tag(name=tag_name)
        self.tags.append(relation)
        return True

    class PaperHasTag(Serializable, db.Model):
        tag_name = Column(String(128), ForeignKey('tag.name'), primary_key=True)
        paper_id = Column(String(128), ForeignKey('paper.id'), primary_key=True)
        is_primary = Column(db.Boolean, default=False)
        tag = relationship("Tag")
        _dict_fields = ['is_primary', 'tag_name']


class Log(Serializable, db.Model):
    __tablename__ = 'log'
    id = Column(Integer, Sequence('log_id'), primary_key=True)
    created_at = Column(DateTime, default=now)
    level = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("User", backref='logs')
    message = Column(Text)
    trace = Column(Text)
    ip = Column(String(138))
    method = Column(Text)
    api_name = Column(Text)

    _dict_fields = ['id', 'created_at', 'level', 'user_id', 'message', 'trace', 'ip', 'method', 'api_name']

    def __init__(self, user_id, role_id, api_name, method, message, ip='unknown', trace='', level=1):
        self.role_id = role_id
        self.user_id = user_id
        self.level = level
        self.api_name = api_name
        self.method = method
        self.trace = trace
        self.message = message
        self.ip = ip


def init_db(app):
    app.config.from_object('config')
    db.init_app(app)

    from utils.log_utils import logger
    logger.warning('db initialised')

    db.create_all()
    try:
        roles = [
            Role('reader'),
            Role('master'),
            Role('grandmaster')
        ]
        users = [
            User('root', 'Passw0rd', 3),
            User('suicca', 'Passw0rd', 2),
        ]

        with open('./models/data.json') as f:
            papers_data = json.load(f)
        for paper in papers_data:
            p = Paper(**paper)
            db.session.add(p)

        db.session.add_all(roles)
        db.session.add_all(users)
        db.session.commit()
    except:
        pass
