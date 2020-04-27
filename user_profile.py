from flask import Blueprint, render_template, request, redirect, url_for, abort, Response, \
    jsonify, send_file, make_response
from flask import Blueprint, render_template
from models import Projects, User, Comment
from forms import EditProjectForm, EditUserForm
import db_session
from flask_login import current_user, login_required
from blog import delete_project
from main import handle_unauth
from very_simple_stats import plot_avg_likes, plot_date_likes, plot_day_likes
import datetime
import io
import base64
from useful_functions import get_recommended_projects, get_popular_projects, delete_project_image

blueprint = Blueprint('user', __name__,
                      template_folder='templates')


def get_user(username):
    '''Получение объекта User по его username'''
    sesion = db_session.create_session()
    user_obj = sesion.query(User).filter_by(username=username).first()
    sesion.close()
    return user_obj


def get_projects(user_id):
    '''Получение проектов юзера по его id'''
    sesion = db_session.create_session()
    projects = sesion.query(Projects).filter_by(owner_id=user_id).all()
    sesion.close()
    return projects


def get_user_comments(user_id):
    '''Получение комментариев которые написал юзер'''
    sesion = db_session.create_session()
    comments = sesion.query(Comment).filter_by(creator_id=user_id).all()
    sesion.close()
    return comments


def check_validation_of_changes(form: EditUserForm, old_email, old_username):
    '''Проверка формы на правильность'''
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


@blueprint.route('/<string:username>/projects/stats/<int:project_id>')
def stats_for_project(username, project_id):
    '''Получение всей статистики по проекту'''
    if current_user.username != username:
        abort(401)
    else:
        img = plot_avg_likes(project_id)
        stats_imgs = [{'base_64': plot_avg_likes(project_id), 'title': 'Average at all times'},
                      {'base_64': plot_date_likes(project_id), 'title': 'Likes at all times'}]
        for img in plot_day_likes(project_id):
            stats_imgs.append({'base_64': img[0], 'title': str(img[1])})
        return render_template('project_simple_stats.html', stats_imgs=stats_imgs)


@blueprint.route('/<string:username>/projects')
def user_projects(username):
    '''Получить все проекы ользователя'''
    user_obj = get_user(username)
    if user_obj:
        projects = get_projects(user_obj.id)
        return render_template('user_profile.html', title=user_obj.username, user=user_obj,
                               viewer=current_user, nav_status='projects', projects=projects)
    else:
        abort(404)


@blueprint.route('/<string:username>/statistic')
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


@blueprint.route('/<string:username>/delete')
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


@blueprint.route('/<string:username>/edit', methods=['GET', 'POST'])
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
