from flask import Blueprint, render_template, request, redirect, url_for, abort, Response, \
    jsonify, send_file, make_response
from flask import Blueprint, render_template
from models import Projects, User
import db_session
from flask_login import current_user, login_required
from blog import delete_project
from very_simple_stats import plot_avg_likes
import datetime
import io
import base64
from useful_functions import get_recommended_projects, get_popular_projects

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


@blueprint.route('/send-img', methods=['GET', 'POST'])
def send_img():
    img = plot_avg_likes([1, 2, 3], [datetime.datetime(2020, 3, 1), datetime.datetime(2020, 3, 20),
                                     datetime.datetime(2020, 3, 28)])
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0, 0)
    img_ase64 = base64.b64encode(output.getvalue()).decode('utf-8')
    popular_projects = get_popular_projects()
    recommended_projects = get_recommended_projects()
    message = request.cookies.get('error_message')
    response = make_response(
        render_template('first_screen.html', title='Home', popular_projects=popular_projects,
                        recommended_projects=recommended_projects,
                        message=message,
                        login=current_user.is_authenticated,
                        bimg=img_ase64))
    response.set_cookie('error_message', '1', max_age=0)
    return response
    # return send_file(output, mimetype='image/png', as_attachment=False)


@blueprint.route('/<string:username>/projects')
def user_projects(username):
    user_obj = get_user(username)
    if user_obj:
        projects = get_projects(user_obj.id)
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='projects', projects=projects)
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
