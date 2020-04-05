import db_session
from models import Projects
from flask import abort


def get_project(id):
    session = db_session.create_session()
    object_project = session.query(Projects).filter(Projects.id == id).first()
    if object_project:
        return object_project
    abort(404)
