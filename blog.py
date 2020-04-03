from flask import Blueprint, render_template, request, redirect, make_response, url_for
from forms import RegisterProjectForm
from models import Projects
import db_session
import datetime

blueprint = Blueprint('blog', __name__,
                      template_folder='templates')


@blueprint.route('/register-project', methods=['GET', 'POST'])
def register_project():
    form = RegisterProjectForm()
    if request.method == 'POST' and form.validate_on_submit():
        project = Projects(name=form.name.data,
                           short_description=form.short_description.data,
                           full_description=form.full_description.data,
                           collaborators=form.collaborators.data)
        sesion = db_session.create_session()
        sesion.add(project)
        sesion.commit()
        sesion.close()
        return redirect(url_for('base'))
    return render_template('register_project.html', form=form, title='Register project')
