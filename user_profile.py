from flask import Blueprint, render_template, request, redirect, url_for, abort, Response, \
    jsonify
from flask import Blueprint, render_template
from models import Projects, User
import db_session
from flask_login import current_user, login_required
from blog import delete_project
from main import handle_unauth

blueprint = Blueprint('user', __name__,
                      template_folder='templates')


def get_user(username):
    sesion = db_session.create_session()
    user_obj = sesion.query(User).filter_by(username=username).first()
    return user_obj


def get_projects(user_id):
    sesion = db_session.create_session()
    projects = sesion.query(Projects).filter_by(owner_id=user_id).all()
    return projects


@blueprint.route('/<string:username>')
def user_info(username):
    user_obj = get_user(username)
    if user_obj:
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='info')
    else:
        abort(404)


@blueprint.route('/projects/<string:username>')
def user_projects(username):
    user_obj = get_user(username)
    if user_obj:
        projects = get_projects(user_obj.id)
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='projects', projects=projects)
    else:
        abort(404)


@blueprint.route('/statistic/<string:username>')
def user_statistics(username):
    user_obj = get_user(username)
    if user_obj:
        statistic = {'total_views': 0, 'total_rates': 0, 'average_rating': 0,
                     'number_of_projects': 0}
        projects = get_projects(user_obj.id)
        if projects:
            for project in projects:
                statistic['total_views'] += project.views
                statistic['total_rates'] += project.num_rates
                statistic['average_rating'] += project.avg_rate
                statistic['number_of_projects'] += 1
            statistic['average_rating'] /= statistic['number_of_projects']
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='statistic', stats=statistic)
    else:
        abort(404)


# Not working now
@blueprint.route('/delete/<string:username>')
@login_required
def delete_user(username):
    user_obj = get_user(username)
    if user_obj:
        if current_user.id == user_obj.id:
            projects = get_projects(user_obj)
            if projects:
                for project in projects:
                    sesion = db_session.create_session()
                    delete_project(sesion, project)
                    sesion.close()
            sesion = db_session.create_session()
            sesion.delete(user_obj)
            sesion.commit()
            sesion.close()
            return redirect('/')
        else:
            return redirect(f'/user/{{username}}')
    else:
        abort(404)
