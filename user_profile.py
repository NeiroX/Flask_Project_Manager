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
    sesion.close()
    return user_obj


def get_projects(user_id):
    sesion = db_session.create_session()
    projects = sesion.query(Projects).filter_by(owner_id=user_id).all()
    sesion.close()
    return projects


def get_user_comments(user_id):
    sesion = db_session.create_session()
    comments = sesion.query(Comment).filter_by(creator_id=user_id).all()
    sesion.close()
    return comments


def check_validation_of_changes(form: EditUserForm, old_email, old_username):
    if len(form.username.data) < 4:
        return ('username', 'Length should be more than 3')
    sesion = db_session.create_session()
    if sesion.query(User).filter(
            User.email == form.email.data).first() and form.email.data != old_email:
        return ('email', 'Email already exists')
    if sesion.query(User).filter(
            User.username == form.username.data).first() and form.username.data != old_username:
        return ('username', 'Username already taken')
    if form.age.data <= 0:
        return ('age', 'Incorrect age')
    if type(form.age.data) != int:
        return ('age', 'Field must be digit')
    return 'OK'


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


@blueprint.route('/statistic/<string:username>')
def user_statistics(username):
    user_obj = get_user(username)
    if user_obj:
        statistic = {'total_rates': 0, 'average_rating': 0,
                     'number_of_projects': 0, 'total_comments': 0}
        projects = get_projects(user_obj.id)
        comments = get_user_comments(user_obj.id)
        if projects:
            for project in projects:
                statistic['total_rates'] += project.num_rates
                statistic['average_rating'] += project.avg_rate
                statistic['number_of_projects'] += 1
            statistic['average_rating'] /= statistic['total_rates']
        statistic['total_comments'] = len(comments) if comments else 0
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='statistic', stats=statistic)
    else:
        abort(404)


@blueprint.route('/delete/<string:username>')
@login_required
def delete_user(username):
    user_obj = get_user(username)
    print('hi')
    if user_obj:
        if current_user.id == user_obj.id:
            projects = get_projects(user_obj.id)
            comments = get_user_comments(user_obj.id)
            sesion = db_session.create_session()
            if projects:
                for project in projects:
                    delete_project_image(project.image_path)
                    sesion.delete(project)
            if comments:
                for comment in comments:
                    sesion.delete(comment)
            handle_unauth()
            sesion.delete(user_obj)
            sesion.commit()
            return redirect('/')
        else:
            return redirect(f'/user/{{username}}')
    else:
        abort(404)


@blueprint.route('/edit/<string:username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    form = EditUserForm()
    if request.method == 'GET':
        user_obj = get_user(username)  # type: User
        if user_obj:
            if user_obj.id == current_user.id:
                form.name.data = user_obj.name
                form.surname.data = user_obj.surname
                form.username.data = user_obj.username
                form.email.data = user_obj.email
                form.description.data = user_obj.description
                form.age.data = user_obj.age
            else:
                return redirect(f'/user/{{username}}')
        else:
            abort(404)
    if form.validate_on_submit() and request.method == 'POST':
        sesion = db_session.create_session()
        user_obj = sesion.query(User).filter_by(username=username).first()  # type: User
        valid_answer = check_validation_of_changes(form, user_obj.email, user_obj.username)
        if valid_answer == 'OK':
            user_obj.name = form.name.data
            user_obj.surname = form.surname.data
            user_obj.username = form.username.data
            user_obj.email = form.email.data
            user_obj.description = form.description.data
            user_obj.age = form.age.data
            sesion.commit()
            return redirect(f'/user/{user_obj.username}')
        else:
            attr = getattr(form, valid_answer[0])
            attr.errors.append(valid_answer[1])
    return render_template('edit_user_profile.html', title='Editing profile', form=form,
                           username=username)
