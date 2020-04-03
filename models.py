import datetime
import sqlalchemy
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
    edit_date = sqlalchemy.Column(sqlalchemy.DateTime)
    rates_5 = sqlalchemy.Column(sqlalchemy.Integer)
    rates_4 = sqlalchemy.Column(sqlalchemy.Integer)
    rates_3 = sqlalchemy.Column(sqlalchemy.Integer)
    rates_2 = sqlalchemy.Column(sqlalchemy.Integer)
    rates_1 = sqlalchemy.Column(sqlalchemy.Integer)
    views = sqlalchemy.Column(sqlalchemy.Integer)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    owner = orm.relationship('User', foreign_keys='Projects.owner_id')
