from flask import Blueprint, render_template, abort
from flask_login import current_user
from models import User, Projects
import db_session

blueprint = Blueprint('users', __name__, template_folder='templates')


@blueprint.route('/show_statstics')
def show_statistics():


@blueprint.route('/<username>')
def show_user(username):
    sesion = db_session.create_session()
    user = sesion.query(User).filter(User.username == username).first()
    if not user:
        return abort(404)
    projects = sesion.query(Projects).filter(Projects.owner_id == user.id).all()
    render_template('show_user.html', user=user, projects=projects)
