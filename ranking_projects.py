from flask import Blueprint, render_template, request, redirect, url_for, abort, session, \
    make_response, jsonify
from db_session import create_session, create_coon
from models import ranked_table, Projects
from flask_login import current_user
from sqlalchemy import insert
import schedule

blueprint = Blueprint('ranking_projects', __name__, template_folder='templates')


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
        print('rank int', rank_int)
        rts = getattr(c_prjct, f'rates_{rank_int}')
        setattr(c_prjct, f'rates_{rank_int}', int(rts) + 1)
        if c_prjct.avg_rate == 0:
            print('Rank for first', rank_int)
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
    print('Add rank', current_user.is_authenticated)
    print(request.args.get('pr_id'), request.args.get('rank'))
    ans = add_to_already_ranked(int(request.args.get('pr_id')), request.args.get('rank'))
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
    '''this function is for returning single project to be displayed as a rated one'''
    sesion = create_session()
    if current_user.is_anonymous:
        '''Unauthorized user. If he has a cookie, return the next project to cookie.
         else return first project from db'''
        last_prjct_id = request.cookies.get('last_project_id', None)
        if last_prjct_id:
            last_prjct_id = int(last_prjct_id) + 1
        else:
            last_prjct_id = 1
    else:
        '''TODO: Either use knn algorithm for finding best project. or just iterate through user interests'''
        '''Now just returns the same thing as unauthorized'''
        last_prjct_id = request.cookies.get('last_project_id', None)
        if last_prjct_id:
            last_prjct_id = int(last_prjct_id) + 1
        else:
            last_prjct_id = 1
    project = sesion.query(Projects).get(last_prjct_id)
    if not project:
        return None
    return (project, last_prjct_id)


@blueprint.route('/', methods=['GET', 'POST'])
def rank_projects():
    project = choose_project()  # type: Projects
    if not project:
        response = make_response(redirect(url_for('base')))
        response.set_cookie('error_message',
                            '<strong>You have already ranked all the projects</strong>', max_age=60)
        return response
    first_project, new_last_id = project
    response = make_response(render_template('rank_project.html', project=first_project.tojson()))
    response.set_cookie('last_project_id', str(new_last_id))
    return response
