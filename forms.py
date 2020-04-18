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


class ProjectForm(FlaskForm):
    name = StringField('* Project name', validators=[DataRequired()])
    image_field = FileField('Project image')
    short_description = TextAreaField('* Short description', validators=[DataRequired()])
    full_description = TextAreaField('Full description')
    collaborators = StringField(
        'Collaborators')


class RegisterProjectForm(ProjectForm):
    submit = SubmitField('Create project')


class EditProjectForm(ProjectForm):
    submit = SubmitField('Save')


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Leave a comment')
