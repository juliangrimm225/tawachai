from flask import current_app
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt
from app.search import add_to_index, remove_from_index, query_index
from uuid import uuid4

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

OrganisationUsers = db.Table('OrganisationUsers',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('organisation_id', db.Integer, db.ForeignKey('Organisation.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('type', db.String))

GroupUsers = db.Table('GroupUsers',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('Group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('type', db.String))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    projects = db.relationship('Project', backref='created_by', lazy='dynamic')
    nodes_creation = db.relationship('Node', backref='created_by', lazy='dynamic')
    groups = db.relationship('Group', secondary=GroupUsers, backref='Users')
    organisations = db.relationship('Organisation', secondary=OrganisationUsers, backref='Users')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time()+expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Project(SearchableMixin, db.Model):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    nodes = db.relationship('Node', backref='project', lazy='dynamic')

    def __repr__(self):
        return '<Project {}>'.format(self.name)

    def avatar(self, size):
        digest = md5(str(self.name.lower()+str(self.timestamp).lower()).encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

def uid_gen() -> str:
    uid = str(uuid4())
    return "{}@{}.org".format(uid, uid[:4])

class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, default=uid_gen())
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(140))
    end = db.Column(db.DateTime, default=datetime.utcnow())
    completed = db.Column(db.String(32))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<Node {}>'.format(self.name)

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', secondary=OrganisationUsers, backref='Organisation')

    def avatar(self, size):
        digest = md5(str(self.name.lower()+str(self.timestamp).lower()).encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

        
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', secondary=OrganisationUsers, backref='Group')

    def avatar(self, size):
        digest = md5(str(self.name.lower()+str(self.timestamp).lower()).encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

