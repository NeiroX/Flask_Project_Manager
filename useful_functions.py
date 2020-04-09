from flask import Flask, render_template, request, make_response, abort, url_for, redirect
from forms import RegisterForm
from flask_login import LoginManager, current_user
from models import User, Projects
from werkzeug.utils import secure_filename
import os
import authen
import errors
import blog
from PIL import Image
import db_session


def get_popular_projects():
    sesion = db_session.create_session()

    return sesion.query(Projects).all()


def get_recommended_projects():
    sesion = db_session.create_session()
    return sesion.query(Projects).all()


def resize_image(img_url, w, h):
    try:
        image = Image.open(img_url)
        new_image = image.resize((w, h))
        new_image.save(img_url)
        return 'OK'
    except Exception as e:
        return e
import db_session
from models import Projects
from flask import abort


def get_project(id):
    sesion = db_session.create_session()
    object_project = sesion.query(Projects).get(id)
    if object_project:
        return object_project
    abort(404)
