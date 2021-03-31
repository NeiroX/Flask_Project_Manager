from flask import Blueprint, render_template, request, redirect, url_for, abort, session, \
    make_response, jsonify
from db_session import create_session, create_coon
from models import ranked_table, Projects
from flask_login import current_user
from sqlalchemy import insert, func, select
import schedule
from useful_functions import add_comment

blueprint = Blueprint('ranking_projects', __name__, template_folder='templates')
ADMIN = 'A'


def add_to_already_ranked(id, rank):
    if current_user.is_authenticated:
        conn = create_coon()
        ins = ranked_table.insert().values(project_id=id, user_id=current_user.id, rank=rank)
        conn.execute(ins)
        sesion = create_session()
        c_prjct = sesion.query(Projects).get(id)
        if not c_prjct:
            return {'response': 404}
        rank_int = int(rank[-1])
        rts = getattr(c_prjct, f'rates_{rank_int}')
        setattr(c_prjct, f'rates_{rank_int}', int(rts) + 1)
        if c_prjct.avg_rate == 0:
            c_prjct.avg_rate = rank_int
        else:
            c_prjct.avg_rate = (c_prjct.avg_rate * c_prjct.num_rates + rank_int) / (
                    1 + c_prjct.num_rates)
        c_prjct.num_rates += 1
        sesion.commit()
        return {'response': 200}
    return {'response': 403}


@blueprint.route('/add_rank', methods=['GET', 'POST'])
def add():
    pr_id = int(request.args.get('pr_id'))
    try:
        add_comment(pr_id, current_user.id, request.args.get('text'))
    except:
        print('Comment not added')
    ans = add_to_already_ranked(pr_id, request.args.get('rank'))
    if ans['response'] == 200:
        next_project_ans = choose_project()
        if not next_project_ans:
            url = url_for('base')
            return jsonify({'url': url})
        next_project, new_last_id = next_project_ans
        html_template = render_template('rank_project.html', project=next_project.tojson())
        return html_template
    return jsonify(ans)


def choose_project():
    sesion = create_session()
    if current_user.is_anonymous:
        last_prjct_id = request.cookies.get('last_project_id', None)
        if last_prjct_id:
            last_prjct_id = int(last_prjct_id) + 1
        else:
            last_prjct_id = 1
    else:
        last_prjct_id = request.cookies.get('last_project_id', None)
        if last_prjct_id:
            last_prjct_id = int(last_prjct_id) + 1
        else:
            last_prjct_id = 1
        project = sesion.query(Projects).get(last_prjct_id)
        try:
            max_id = sesion.query(func.max(Projects.id))[0][0]
        except:
            max_id = 2
        s = select([ranked_table]).where(ranked_table.c.user_id == current_user.id)
        conn = create_coon()
        ranked_projects = [row[1] for row in conn.execute(s)]
        while (not project or project.id in ranked_projects) and last_prjct_id <= max_id:
            last_prjct_id += 1
            project = sesion.query(Projects).get(last_prjct_id)
    if not project:
        return None
    return (project, last_prjct_id)


@blueprint.route('/', methods=['GET', 'POST'])
def rank_projects():
    project = choose_project()  # type: Projects
    print(project)
    if not project:
        response = make_response(redirect(url_for('base')))
        response.set_cookie('error_message',
                            '<strong>You have already ranked all the projects</strong>', max_age=60)
        return response
    first_project, new_last_id = project
    response = make_response(render_template('rank_project.html', title='Rate',
                                             project=first_project.tojson()))
    response.set_cookie('last_project_id', str(new_last_id))
    return response
