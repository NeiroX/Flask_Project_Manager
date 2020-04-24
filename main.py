from flask import Flask, render_template, request, make_response, url_for, redirect, jsonify
from flask_login import LoginManager, current_user
from models import User
import os
import authen
import errors
import blog
import db_session
import ranking_projects
import _thread
from useful_functions import (get_popular_projects,
                              get_recommended_projects,
                              write_new_likes)
import datetime
import schedule
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask_project_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/imgs')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365 * 10)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    sesion = db_session.create_session()
    return sesion.query(User).get(user_id)


@app.route('/')
def base():
    popular_projects = get_popular_projects()
    recommended_projects = get_recommended_projects()
    message = request.cookies.get('error_message')
    response = make_response(
        render_template('first_screen.html', popular_projects=popular_projects,
                        recommended_projects=recommended_projects,
                        message=message, login=current_user.is_authenticated))
    response.set_cookie('error_message', '1', max_age=0)
    return response


@app.route('/like/', methods=['POST'])
def like():
    print('Like this project', request.form['prj_id'])
    return jsonify({'status': 'OK'})


@app.route('/user/<username>')
def get_user(username):
    return render_template('')


@login_manager.unauthorized_handler
def handle_unauth():
    print('Unautharized')
    resp = make_response(
        redirect(url_for('authen.login', next=request.url, login_message='Login required')))
    return resp


@app.before_request
def before_req():
    print(current_user.is_authenticated)


def schedule_thread():
    schedule.every().day.do(write_new_likes)
    while True:
        schedule.run_pending()
        print('a')


if __name__ == '__main__':
    db_session.global_init("db.sqlite")

    th=threading.Thread(target=schedule_thread)
    app.register_blueprint(authen.blueprint)
    app.register_blueprint(errors.blueprint)
    app.register_blueprint(blog.blueprint, url_prefix='/project')
    app.register_blueprint(ranking_projects.blueprint, url_prefix='/rank-projects')
    app.run(port=8080, host='127.0.0.1')
