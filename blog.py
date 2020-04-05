from flask import Blueprint, render_template, request, redirect, make_response, url_for
from sqlalchemy import func
from forms import RegisterProjectForm
from models import Projects, User
import db_session
import datetime
from main import app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os

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
            filename = f'{current_user.id}_{int(last_id[0])+1}.' + image.filename.rsplit('.')[1]
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], os.path.join('project_imgs', filename)))
        for username in form.collaborators.data.split(', '):
            user = sesion.query(User).filter(User.username == username.strip()[1:]).first()
            if user:
                project.collaborators.append(user)
        sesion.add(project)
        sesion.commit()
        sesion.close()
        return redirect(url_for('base'))
    return render_template('register_project.html', form=form, title='Register project')
