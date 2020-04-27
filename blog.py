from flask import Blueprint, render_template, request, redirect, url_for, abort, session, Response, \
    jsonify
from forms import RegisterProjectForm, CommentForm
from models import Projects, User, Comment, Tags, project_tag_table
from flask import Blueprint, render_template, request, redirect, make_response, url_for, abort
from sqlalchemy import func
from forms import RegisterProjectForm, EditProjectForm
from models import Projects, User, association_comments
import db_session
import datetime
from main import app, handle_unauth
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import requests
import os
import subprocess
from useful_functions import get_project, resize_image
from analyze_description import analyze_description

blueprint = Blueprint('blog', __name__,
                      template_folder='templates')


# Добавление ключевых слов(тегов) в бд ???
def add_tags_to_project(prj_id, tags):
    sesion = db_session.create_session()
    for tag_name in tags:
        tag = sesion.query(Tags).filter(Tags.interest == tag_name).first()
        if not tag:
            new_tag = Tags(interest=tag_name)
            sesion.add(new_tag)
            sesion.commit()
            last_id = sesion.query(func.max(Tags.id)).one()[0]
            last_id = last_id if last_id else 1
        else:
            last_id = tag.id
        conn = db_session.create_coon()
        ins = project_tag_table.insert().values(project_id=prj_id, tag_id=last_id)
        conn.execute(ins)
    return


# Проверка информации регистрации проекта
def check_project(form):
    if len(form.short_description.data) >= 150:
        return 'short_description', 'Length of short description should be less than 150'
    return 'OK'


# Получение комментариев к проекту
def get_project_comments(project_id):
    sesion = db_session.create_session()
    comments = sesion.query(Comment).filter_by(project_id=project_id).all()
    sesion.close()
    return comments


# Удаление аватарок к проекту
def delete_project_image(img_name):
    if img_name.split()[-1] != 'no_project_image.jpg':
        try:
            os.remove(img_name)
        except Exception as e:
            print(e)


# Проверка тегов ???
@blueprint.route('/register/check', methods=['GET', 'POST'])
@login_required
def check_tags():
    tags = request.args.get('tags').split(',')
    if request.method == 'POST':
        wrong = [int(key[6:]) - 1 for key in request.form.keys()]
        add_tags_to_project(int(request.args.get('id')),
                            [tags[i] for i in range(len(tags)) if i not in wrong])
        return redirect(url_for('base'))
    return render_template('check_tags.html', tags=tags)


# Реристрация проекта(форма и добавление в бд)
@blueprint.route('/register', methods=['GET', 'POST'])
@login_required
def register_project():
    form = RegisterProjectForm()
    if request.method == 'POST' and form.validate_on_submit():
        project = Projects(name=form.name.data,
                           short_description=form.short_description.data,
                           full_description=form.full_description.data,
                           owner_id=current_user.id)
        resp = check_project(form)
        # checking is all data in form is good
        if resp != 'OK':
            err_attr = getattr(form, resp[0])
            err_attr.errors.append(resp[1])
            return render_template('register_project.html', form=form, title='Register project')
        sesion = db_session.create_session()
        # getting this project id
        last_id = sesion.query(func.max(Projects.id)).one()

        # saving image for this project
        image = request.files.get('image_field')
        if not last_id[0]:
            last_id = 1
        else:
            last_id = int(last_id[0]) + 1
        if image and image.filename.rsplit('.')[1] in ['png', 'jpg', 'jpeg']:
            filename = f'{current_user.id}_{last_id}.jpg'
            global_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                            os.path.join('project_imgs', filename))
            image.save(global_file_path)
            project.image_path = url_for('static', filename=f'imgs/project_imgs/{filename}')
        else:
            project.image_path = url_for('static', filename='imgs/project_imgs/no_project_image.jpg')
        for username in form.collaborators.data.split(', '):
            user = sesion.query(User).filter(User.username == username.strip()[1:]).first()
            if user:
                project.collaborators.append(user)
        sesion.add(project)
        sesion.commit()
        sesion.close()

        probable_tags = analyze_description(last_id)
        subprocess.call(f'python analyze_description.py {last_id}', shell=True)
        response = make_response(
            redirect(url_for('blog.check_tags', id=str(last_id), tags=','.join(probable_tags))))
        return response
    return render_template('register_project.html', form=form, title='Register project')


# Просмотр проекта и форма комментариев
@blueprint.route('/show/<int:id>', methods=['GET', 'POST'])
def view_project(id):
    project = get_project(id)  # type: Projects
    if project:
        form = CommentForm()
        if request.method == 'POST' and current_user.is_anonymous:
            return handle_unauth()
        comment_ans = add_comment(project, form)
        if comment_ans == 'OK':
            sesion = db_session.create_session()
            com = sesion.query(Comment).filter(
                Comment.id == sesion.query(func.max(Comment.id))).first()
            sesion.close()
            project.comments.append(com)
            form.text.data = ''
        info = project.__dict__
        comments_prev_list = get_project_comments(id)
        sesion = db_session.create_session()
        comments = [(sesion.query(User).get(comment.creator_id), comment) for
                    comment in
                    comments_prev_list] if comments_prev_list else []
        info['create_date'] = info['create_date'].ctime()
        if info['edit_date'] is not None:
            info['edit_date'] = info['edit_date']
        return render_template('blog_view.html', title=project.name,
                               image=project.image_path,
                               form=form,
                               author=project.owner.username, viewer=current_user,
                               comments_list=comments, **info)
    else:
        abort(404)


# Добавление комментариев в бд
@login_required
def add_comment(project, form):
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.is_anonymous:
            return redirect(f'/project/show/{project.id}')
        comment = Comment(text=form.text.data.strip(),
                          creator_id=current_user.id,
                          project_id=project.id)
        sesion = db_session.create_session()
        sesion.add(comment)
        sesion.commit()
        sesion.close()
        return 'OK'
    return None


# Функция удаление проектов и их содержимого
@blueprint.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(id):
    project = get_project(id)
    if project and current_user == project.owner or current_user in project.collaborators:
        comments = get_project_comments(project.id)
        img_name = project.image_path
        sesion = db_session.create_session()
        if comments:
            for comment in comments:
                sesion.delete(comment)
        sesion.delete(project)
        sesion.commit()
        delete_project_image(img_name)
    else:
        abort(404)
    return redirect('/')


# Изменение данных проекта и сохранение их в бд
@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    form = EditProjectForm()
    if request.method == 'GET':
        project = get_project(id)  # type: Projects
        if project:
            form.name.data = project.name
            form.short_description.data = project.short_description
            form.full_description.data = project.full_description
            form.collaborators.data = 'Only owner now'
            form.image_field.data = project.image_path
        else:
            abort(404)
    if form.validate_on_submit():
        sesion = db_session.create_session()
        project = sesion.query(Projects).get(id)  # type: Projects
        if project:
            project.name = form.name.data
            project.short_description = form.short_description.data
            project.full_description = form.full_description.data
            project.edit_date = datetime.datetime.now()
            last_id = sesion.query(func.max(Projects.id)).one()
            image = request.files.get('image_field')
            if image and image.filename.rsplit('.')[1] in ['png', 'jpg', 'jpeg']:
                res = last_id[0]
                if not res:
                    res = 1
                filename = f'{current_user.id}_{res + 1}.jpg'
                image.save(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 os.path.join('project_imgs', filename)))
                project.image_path = url_for('static',
                                             filename=f'imgs/project_imgs/{current_user.id}_{res + 1}.jpg')
            else:
                project.image_path = url_for('static',
                                             filename='imgs/project_imgs/no_project_image.jpg')

            sesion.commit()
            # subprocess.call(f'python3 analyze_description.py {last_id} --editing', shell=True)
            return redirect(f'/project/show/{id}')
        else:
            abort(404)
    return render_template('edit_project.html', title='Edit project', form=form, id=id)
