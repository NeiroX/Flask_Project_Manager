from flask import Blueprint, render_template, request, redirect, make_response, url_for
from forms import RegisterUserForm, LoginForm
from flask_login import login_user, logout_user
from models import User
import db_session
import datetime

blueprint = Blueprint('authen', __name__,
                      template_folder='templates')


# Функция проверки информации входа в аккаунт(на существующий username, правильность пароля)
def check_user(form):
    sesion = db_session.create_session()
    user = sesion.query(User).filter(
        (User.email == form.username_email.data) | (
                User.username == form.username_email.data)).first()
    if not user:
        return ('username_email', 'User does not exist')
    if not user.check_password(form.password.data):
        return ('password', 'Wrong password')
    return 'OK'


# Функция проверки информации регистарции пользователя
def check_new_user(form: RegisterUserForm):
    # длина логина >4
    if len(form.username.data) < 4:
        return ('username', 'Length should be more than 3')
    sesion = db_session.create_session()
    # Существующий email
    if sesion.query(User).filter(User.email == form.email.data).first():
        return ('email', 'Email already exists')
    # Существующий username
    if sesion.query(User).filter(User.username == form.username.data).first():
        return ('username', 'Username already taken')
    # Правильный возраст
    if type(form.age.data) != int:
        return ('age', 'Field must be digit')
    if form.age.data <= 0:
        return ('age', 'Incorrect age')
    return 'OK'


# Регистрация(форма и добавление в бд)
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    # вывод списка стран
    countries_list = [(country, country) for country in
                      [line.strip() for line in open('data/countries.txt').readlines()]]
    form.country.choices = countries_list
    if request.method == 'POST' and form.validate_on_submit():
        ans = check_new_user(form)
        if ans != 'OK':
            attr = getattr(form, ans[0])
            attr.errors.append(ans[1])
            return render_template('register.html', form=form, title='Register')
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    username=form.username.data,
                    email=form.email.data,
                    description=form.description.data,
                    country=form.country.data,
                    age=form.age.data,
                    register_date=datetime.datetime.now())
        user.set_password(form.password.data)
        sesion = db_session.create_session()
        sesion.add(user)
        sesion.commit()
        sesion.close()
        return redirect(url_for('authen.login'))
    return render_template('register.html', form=form, title='Register')


# Вод в аккаунт и работа с куки
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Форма логина. Если пользователя перекинуло из-за того что он не авторизован -
    буде  '''
    next = request.args.get('next', url_for('base'))
    messg = request.args.get('login_message', '')
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
            resp = make_response(
                render_template('login.html', message_login=messg, form=form, title='Login'))
            resp.set_cookie('login_tries', str(login_tries + 1), max_age=60 * 2)
            return resp
        sesion = db_session.create_session()
        user = sesion.query(User).filter((User.email == form.username_email.data) | (
                User.username == form.username_email.data)).first()
        login_user(user, remember=form.remember_me.data)
        return redirect(next)
    form.username_email.data = 'username'
    resp = make_response(
        render_template('login.html', message_login=messg, form=form, title='Login'))
    resp.set_cookie('login_tries', str(login_tries + 1), max_age=60 * 2)
    return resp


# Функиця выхода
@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authen.login'))
