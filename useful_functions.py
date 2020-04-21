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
from sqlalchemy.orm import lazyload, subqueryload


def get_popular_projects():
    sesion = db_session.create_session()
    return sesion.query(Projects).options(subqueryload(Projects.owner)).limit(5).all()


def get_recommended_projects():
    sesion = db_session.create_session()
    return sesion.query(Projects).options(subqueryload(Projects.owner)).limit(5).all()


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
from PIL import Image
import os


def get_project(id):
    sesion = db_session.create_session()
    object_project = sesion.query(Projects).get(id)
    if object_project:
        return object_project
    abort(404)


# def get_comments(project_id):
#     session = db_session.create_session()
#     comments


def resize_image(image_name, w, h):
    try:
        path = os.path.join(os.getcwd(), os.path.join('static/imgs/project_imgs',
                                                      image_name))
        image = Image.open(path)
        new_image = image.resize((w, h))
        new_image.save(path)
        return 'OK'
    except Exception as e:
        return e
