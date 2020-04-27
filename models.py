import datetime
import sqlalchemy
from flask import url_for
from sqlalchemy import orm
from db_session import SqlAlchemyBase, create_coon
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
import json


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    country = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime)
    prjcts = sqlalchemy.Column(sqlalchemy.String)

    def tojson(self, *args):
        json_ls = {}
        if len(args) > 0:
            for attr in args:
                json_ls[attr] = getattr(self, attr)
        else:
            for attr in ['name', 'surname', 'username', 'email', 'country', 'age']:
                json_ls[attr] = getattr(self, attr)
        print('user to json', json_ls)
        return json_ls

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Projects(SqlAlchemyBase):
    __tablename__ = 'projects'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    short_description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    full_description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    image_path = sqlalchemy.Column(sqlalchemy.String)
    edit_date = sqlalchemy.Column(sqlalchemy.DateTime)
    rates_5 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rates_4 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rates_3 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rates_2 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rates_1 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    num_rates = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    avg_rate = sqlalchemy.Column(sqlalchemy.Float, default=0)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    points = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    owner = orm.relationship('User', foreign_keys='Projects.owner_id', lazy='subquery')  # type: User
    collaborators = orm.relation('User', secondary='association_collabs', backref='projects')
    comments = orm.relationship('Comment', backref='projects', lazy='dynamic')

    def tojson(self, *args):
        json_ls = {}
        if len(args) > 0:
            for arg in args:
                json_ls[arg] = getattr(self, arg)
        else:
            for attr in ['id', 'name', 'short_description', 'full_description', 'create_date',
                         'image_path', 'edit_date']:
                json_ls[attr] = getattr(self, attr)
            owner_json = self.owner.tojson()
            json_ls.update({'owner_' + key: owner_json[key] for key in owner_json.keys()})
        print('project to json', json_ls)
        return json_ls

    def filter_text(self):
        words = []
        for word in self.short_description.split():
            word = word.strip()
            if not word[-1].isalpha():
                if len(word) == 1:
                    continue
                else:
                    word = word[:-1]
            words.append(word.lower())
        return words


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    project_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('projects.id'))
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def tojson(self, *args):
        json_ls = {}
        if len(args) > 0:
            for attr in args:
                json_ls[attr] = getattr(self, attr)
        else:
            for attr in ['id', 'text', 'creator_id', 'create_date', 'project_id', 'likes']:
                json_ls[attr] = getattr(self, attr)
        print('comment to json', json_ls)
        return json_ls


class Tags(SqlAlchemyBase):
    __tablename__ = 'tags'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    interest = sqlalchemy.Column(sqlalchemy.String, unique=True)


association_collabs = sqlalchemy.Table('association_collabs', SqlAlchemyBase.metadata,
                                       sqlalchemy.Column('project_id', sqlalchemy.Integer,
                                                         sqlalchemy.ForeignKey('projects.id')),
                                       sqlalchemy.Column('collab_id', sqlalchemy.Integer,
                                                         sqlalchemy.ForeignKey('users.id')))

association_comments = sqlalchemy.Table('association_comments', SqlAlchemyBase.metadata,
                                        sqlalchemy.Column('project_id', sqlalchemy.Integer,
                                                          sqlalchemy.ForeignKey('projects.id')),
                                        sqlalchemy.Column('comment_id', sqlalchemy.Integer,
                                                          sqlalchemy.ForeignKey('comments.id')))

ranked_table = sqlalchemy.Table('ranked_table', SqlAlchemyBase.metadata,
                                sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True,
                                                  autoincrement=True),
                                sqlalchemy.Column('project_id', sqlalchemy.Integer),
                                sqlalchemy.Column('user_id', sqlalchemy.Integer),
                                sqlalchemy.Column('rank', sqlalchemy.Integer))

user_interest_table = sqlalchemy.Table('user_interest_table', SqlAlchemyBase.metadata,
                                       sqlalchemy.Column('user_id', sqlalchemy.Integer),
                                       sqlalchemy.Column('tag_id', sqlalchemy.Integer))

project_tag_table = sqlalchemy.Table('project_tag_table', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('project_id', sqlalchemy.Integer),
                                     sqlalchemy.Column('tag_id', sqlalchemy.Integer))
