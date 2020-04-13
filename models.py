import datetime
import sqlalchemy
from flask import url_for
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    country = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime)
    prjcts = sqlalchemy.Column(sqlalchemy.String)

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
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    owner = orm.relationship('User', foreign_keys='Projects.owner_id')
    collaborators = orm.relation('User', secondary='association_collabs', backref='projects')
    comments = orm.relationship('Comment', backref='projects', lazy='dynamic')

    def filter_text(self):
        words = []
        for word in self.full_description.split(' '):
            word = word.strip()
            if not word.isalpha():
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
