from flask import Blueprint, render_template, request, redirect, make_response, url_for
from forms import RegisterForm, LoginForm
from flask_login import login_user, current_user, logout_user
from models import User
import db_session
import datetime

blueprint = Blueprint('authen', __name__,
                      template_folder='templates')


def check_user(form):
    sesion = db_session.create_session()
    user = sesion.query(User).filter(
        (User.email == form.username_email.data) | (
                User.username == form.username_email.data)).first()
    if not user:
        return ('username', 'User does not exist')
    if not user.check_password(form.password.data):
        return ('password', 'Wrong password')
    return 'OK'


def check_new_user(form: RegisterForm):
    if len(form.username.data) < 4:
        return ('username', 'Length should be more than 3')
    sesion = db_session.create_session()
    if sesion.query(User).filter(User.email == form.email.data).first():
        return ('email', 'Email already exists')
    if sesion.query(User).filter(User.username == form.username.data).first():
        return ('username', 'Username already taken')
    if form.age.data <= 0:
        return ('age', 'Incorrect age')
    if type(form.age.data) != int:
        return ('age', 'Field must be digit')
    return 'OK'


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    countries_list = [(country[0], country[1]) for country in
                      enumerate([line.strip() for line in open('Data/countries.txt').readlines()])]
    form.country.choices = countries_list
    if request.method == 'POST' and form.validate_on_submit():
        ans = check_new_user(form)
        print(ans)
        if ans != 'OK':
            attr = getattr(form, ans[0])
            attr.errors.append(ans[1])
            return render_template('register.html', form=form, title='Register')
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    username=form.username.data,
                    email=form.email.data,
                    country=form.country.data,
                    age=form.age.data,
                    register_date=datetime.datetime.now())
        user.set_password(form.password.data)
        sesion = db_session.create_session()
        sesion.add(user)
        sesion.commit()
        sesion.close()
        return redirect('base')
    return render_template('register.html', form=form, title='Register')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    login_tries = int(request.cookies.get('login_tries', 0))
    if login_tries == 4:
        resp = make_response(redirect(url_for('base')))
        resp.set_cookie('error_message', '<strong>Too much tries!'
                                         '</strong> Try again in 2 minutes', max_age=60)
        return resp
    if request.method == 'POST' and form.validate_on_submit():
        ans = check_user(form)
        if ans != 'OK':
            attr = getattr(form, ans[0])
            attr.errors.append(ans[1])
            resp = make_response(render_template('login.html', form=form, title='Login'))
            resp.set_cookie('login_tries', str(login_tries + 1), max_age=60 * 2)
            return resp
        sesion = db_session.create_session()
        user = sesion.query(User).filter((User.email == form.username_email.data) | (
                User.username == form.username_email.data)).first()
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('base'))
    resp = make_response(render_template('login.html', form=form, title='Login'))
    resp.set_cookie('login_tries', str(login_tries + 1), max_age=60 * 2)
    return resp


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authen.login'))
