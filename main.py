from flask import Flask, render_template, request, make_response, abort
from forms import RegisterForm
from flask_login import LoginManager, current_user
from models import User
from werkzeug.utils import secure_filename
import os
import authen
import errors
import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask_project_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/imgs')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    sesion = db_session.create_session()
    return sesion.query(User).get(user_id)


@app.route('/')
def base():
    message = request.cookies.get('error_message')
    response = make_response(render_template('base.html', message=message))
    response.set_cookie('error_message', '1', max_age=0)
    return response


@app.route('/hello')
def abor():
    abort(404)




@app.before_request
def before_req():
    print(current_user.is_authenticated)


if __name__ == '__main__':
    db_session.global_init("db.sqlite")
    app.register_blueprint(authen.blueprint)
    app.register_blueprint(errors.blueprint)
    app.run()
