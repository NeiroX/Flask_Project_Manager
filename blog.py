from flask import Blueprint, render_template, request, redirect, url_for, abort
from forms import RegisterProjectForm, CommentForm
from models import Projects, User, Comment
from flask import Blueprint, render_template, request, redirect, make_response, url_for, abort
from sqlalchemy import func
from forms import RegisterProjectForm
from models import Projects, User
import db_session
import datetime
from main import app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os
from flask_login import current_user
from useful_functions import get_project, resize_image

blueprint = Blueprint('blog', __name__,
                      template_folder='templates')


@blueprint.route('/register-project', methods=['GET', 'POST'])
@login_required
def register_project():
    form = RegisterProjectForm()
    if request.method == 'POST' and form.validate_on_submit():
        project = Projects(name=form.name.data,
                           short_description=form.short_description.data,
                           full_description=form.full_description.data,
                           owner_id=current_user.id)
        sesion = db_session.create_session()
        last_id = sesion.query(func.max(Projects.id)).one()
        image = request.files.get('image_field')
        if image and image.filename.rsplit('.')[1] in ['png', 'jpg', 'jpeg']:
            filename = f'{current_user.id}_{int(last_id[0])+1}.jpg'
            filename = os.path.join(app.config['UPLOAD_FOLDER'], os.path.join('project_imgs', filename))
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
        return redirect(url_for('base'))
    return render_template('register_project.html', form=form, title='Register project')


@blueprint.route('/project/<int:id>', methods=['GET', 'POST'])
def view_project(id):
    project = get_project(id)  # type: Projects
    if project:
        form = CommentForm()
        comment_ans = add_comment(project, form)
        print('Went put')
        if comment_ans == 'OK':
            sesion = db_session.create_session()
            com=sesion.query(Comment).filter(Comment.id == sesion.query(func.max(Comment.id))).first()
            project.comments.append(com)
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
                               author=project.owner.username, **info)
    else:
        abort(404)


def add_comment(project, form):
    if request.method == 'POST' and form.validate_on_submit():
        comment = Comment(text=form.text.data,
                          creator_id=current_user.id,
                          project_id=project.id)
        sesion = db_session.create_session()
        sesion.add(comment)
        sesion.commit()
        sesion.close()
        return 'OK'
    return None
