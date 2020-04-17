from flask import Blueprint, render_template, request, redirect, url_for, abort, session
from forms import RegisterProjectForm, CommentForm
from models import Projects, User, Comment
from flask import Blueprint, render_template, request, redirect, make_response, url_for, abort
from sqlalchemy import func
from forms import RegisterProjectForm, EditProjectForm
from models import Projects, User
import db_session
import datetime
from main import app, handle_unauth
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
import subprocess
from flask_login import current_user
from useful_functions import get_project, resize_image

blueprint = Blueprint('blog', __name__,
                      template_folder='templates')


@blueprint.route('/register-project', methods=['GET', 'POST'])
@login_required
def register_project():
    print(current_user.id)
    form = RegisterProjectForm()
    if request.method == 'POST' and form.validate_on_submit():
        project = Projects(name=form.name.data,
                           short_description=form.short_description.data,
                           full_description=form.full_description.data,
                           owner_id=current_user.id)
        sesion = db_session.create_session()
        last_id = sesion.query(func.max(Projects.id)).one()
        image = request.files.get('image_field')
        if not last_id[0]:
            last_id = 1
        else:
            last_id = int(last_id[0]) + 1
        if image and image.filename.rsplit('.')[1] in ['png', 'jpg', 'jpeg']:
            filename = f'{current_user.id}_{last_id}.jpg'
            filename = os.path.join(app.config['UPLOAD_FOLDER'],
                                    os.path.join('project_imgs', filename))
            image.save(filename)
            project.image_path = filename
        else:
            project.image_path = url_for('static', filename='imgs/project_imgs/no_project_image.jpg')
        for username in form.collaborators.data.split(', '):
            user = sesion.query(User).filter(User.username == username.strip()[1:]).first()
            if user:
                project.collaborators.append(user)
        sesion.add(project)
        sesion.commit()
        sesion.close()
        print('subprocess with last_id:', last_id)
        subprocess.call(f'python3 analyze_description.py {last_id}', shell=True)
        return redirect(url_for('base'))
    return render_template('register_project.html', form=form, title='Register project')


@blueprint.route('/project/<int:id>', methods=['GET', 'POST'])
def view_project(id):
    project = get_project(id)  # type: Projects
    print()
    if project:
        form = CommentForm()
        if request.method == 'POST' and current_user.is_anonymous:
            return handle_unauth()
        comment_ans = add_comment(project, form)
        print('Went put')
        if comment_ans == 'OK':
            sesion = db_session.create_session()
            com = sesion.query(Comment).filter(
                Comment.id == sesion.query(func.max(Comment.id))).first()
            project.comments.append(com)
            if not session.get('already_seen', False):
                project.views += 1
            print('This ok')
            print(com.text)
            sesion.commit()

        info = project.__dict__
        print(info)
        print('Date', project.create_date)
        info['create_date'] = info['create_date'].ctime()
        return render_template('blog_view.html', title=project.name,
                               image=project.image_path,
                               form=form,
                               author=project.owner.username, viewer=current_user, **info)
    else:
        abort(404)


@login_required
def add_comment(project, form):
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.is_anonymous:
            return None
        comment = Comment(text=form.text.data,
                          creator_id=current_user.id,
                          project_id=project.id)
        sesion = db_session.create_session()
        sesion.add(comment)
        sesion.commit()
        sesion.close()
        return 'OK'
    return None


@app.route('/project_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_news(id):
    project = get_project(id)
    if project:
        sesion = db_session.create_session()
        sesion.delete(project)
        sesion.commit()
    else:
        abort(404)
    return redirect('/')


@blueprint.route('/project_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    form = EditProjectForm()
    if request.method == 'GET':
        sesion = db_session.create_session()
        project = get_project(id)  # type: Projects
        if project:
            form.name.data = project.name
            form.short_description.data = project.short_description
            form.full_description.data = project.full_description
            form.collaborators.data = 'Only owner now'
            # form.image_field.data = open(project.image_path)
        else:
            abort(404)
    if form.validate_on_submit():
        sesion = db_session.create_session()
        project = get_project(id)  # type: Projects
        if project:
            project.name = form.name.data
            project.short_description = form.short_description.data
            project.full_description = form.full_description.data

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
            return redirect('/')
        else:
            abort(404)
    return render_template('edit_project.html', title='Edit project', form=form)
