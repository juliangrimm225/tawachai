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
from app.graphs import Graph

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


class User(UserMixin, db.Model):
    """ This class describes the user """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    projects = db.relationship('Project', backref='created_by', lazy='dynamic')
    nodes_creation = db.relationship('Node', backref='created_by', lazy='dynamic')

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

class Project(db.Model):
    """A Project contains nodes."""
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

    def graph(self):
        """Returns a dictionary of the whole project that can be used as graph."""

        nodes = self.nodes.all()

        Dict = {}
        for n in nodes:
            Dict[n] = n.sinks()

        graph = Graph(Dict)
        return graph 

    def delete(self):
        for node in self.nodes.all():
            node.delete()
        db.session.delete(self)

def uid_gen() -> str:
    uid = str(uuid4())
    return "{}@{}.org".format(uid, uid[:4])


# Model for Nodes
# Nodes are part of a project
# A project is finished when all nodes are completed
# Nodes have a relationship with each other 

class Edge(db.Model):
    __tablename__ = 'edge'
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    sink_id = db.Column(db.Integer, db.ForeignKey('node.id'))

    def __repr__(self):
        return '<Source {}, Sink {}>'.format(self.source_id, self.sink_id)

class Node(db.Model):
    """Nodes are the basic elements of a project. Each node can only be in one project. They are connected via edges."""
    __tablename__ = 'node'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    name = db.Column(db.String(140))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    edges_sinks = db.relationship('Edge', backref='source', primaryjoin=id==Edge.source_id, lazy='dynamic', cascade="all, delete-orphan")
    edges_sources = db.relationship('Edge', backref='sink', primaryjoin=id==Edge.sink_id, lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Node {}>'.format(self.name)

    def avatar(self, size):
        digest = md5(str(self.name.lower()).lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def sources(self):
        """Create  list of nodes that are sources"""
        lst = []
        edges = self.edges_sources.all()
        for e in edges:
            node = e.source
            lst.append(node)
        return lst

    def sinks(self):
        """Create a list of nodes that are sinks"""
        lst = []
        edges = self.edges_sinks.all()
        for e in edges:
            node = e.sink
            lst.append(node)
        return lst

    def is_sink_for(self, node):
        """Check if self is a sink for node"""
        return self.edges_sources.filter(Edge.source_id == node.id).count()>0

    def is_source_for(self, node):
        """Check if self is a source for node"""
        return self.edges_sinks.filter(Edge.sink_id == node.id).count()>0

    def is_connected_to(self, node):
        """Check if self is either sink or source or identical to node"""
        return self.is_sink_for(node) or self.is_source_for(node) or self == node

    def add_sink(self, node):
        """add a node as a sink"""
        if not self.is_connected_to(node):
            e = Edge()
            e.sink = node
            e.source = self
            self.edges_sinks.append(e)

    def add_source(self, node):
        """add a node as a source"""
        node.add_sink(self)

    def remove_sink(self, node):
        """remove a node as a sink"""
        if self.is_source_for(node):
            e = self.edges_sinks.filter(Edge.sink_id == node.id).first()
            self.edges_sinks.remove(e)

    def remove_source(self, node):
        """remove a node as a source"""
        node.remove_sink(self)
    def delete(self):
        for sink in self.sinks():
            self.remove_sink(sink)
        for source in self.sources():
            self.remove_source(source)
        db.session.delete(self)

        
        

