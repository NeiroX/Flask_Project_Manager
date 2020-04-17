from flask import Blueprint, render_template, request, redirect, url_for, abort, session, \
    make_response
from db_session import create_session, create_coon
from models import ranked_table, Projects
from flask_login import current_user

blueprint = Blueprint('ranking_projects', __name__, template_folder='templates')


def add_to_already_ranked(id):
    if current_user.is_authenticated:
        conn = create_coon()
        ins = ranked_table.insert().values(project_id=id, user_id=current_user.id, ranked=True)
        conn.execute(ins)


def choose_project():
    last_prjct_id = request.cookies.get('last_project_id', None)
    sesion = create_session()
    if current_user.is_anonymous:
        try:
            return (sesion.query(Projects).get(int(last_prjct_id) + 1), int(last_prjct_id) + 1)
        except:
            abort(404)
    else:
        if last_prjct_id:
            c_id = int(last_prjct_id) + 1
        else:
            c_id = 1
        return (sesion.query(Projects).get(c_id), c_id)


@blueprint.route('/', methods=['GET', 'POST'])
def rank_projects():
    front_project, new_last_id = choose_project()  # type: Projects, int
    response = make_response(render_template('rank_project.html', project=front_project.tojson()))
    response.set_cookie('last_project_id', str(new_last_id))
    add_to_already_ranked(new_last_id)
    return response
