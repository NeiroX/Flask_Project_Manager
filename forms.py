from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, IntegerField, SubmitField, FileField, \
    BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message='Bad email')])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password again',
                                   validators=[DataRequired(), EqualTo('password',
                                                                       message='Passwords do not match')])
    country = SelectField('Country', coerce=str, validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username_email = StringField('Username or email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)
    submit = SubmitField('Login')


class RegisterProjectForm(FlaskForm):
    name = StringField('* Project name', validators=[DataRequired()])
    short_description = TextAreaField('* Short description', validators=[DataRequired()])
    full_description = TextAreaField('Full description')
    collaborators = StringField(
        'Collaborators')
    submit = SubmitField('Login')
