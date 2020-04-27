import datetime
from models import likes_in_day_table
import db_session
from models import Projects
from flask import abort
from PIL import Image, ImageDraw
import os
from sqlalchemy.orm import subqueryload
import matplotlib.pyplot as plt
import numpy


def delete_project_image(img_name):
    if img_name.split()[-1] != 'no_project_image.jpg':
        try:
            os.remove(img_name)
        except Exception as e:
            print(e)


def get_popular_projects(num=4):
    sesion = db_session.create_session()
    projects = sesion.query(Projects). \
        options(subqueryload(Projects.owner)). \
        order_by(Projects.avg_rate.desc()). \
        limit(num). \
        all()
    return projects


def get_recommended_projects(num=4):
    sesion = db_session.create_session()
    return sesion.query(Projects). \
        options(subqueryload(Projects.owner)). \
        limit(num). \
        all()


def resize_image(img_url, w, h):
    try:
        image = Image.open(img_url)
        new_image = image.resize((w, h))
        new_image.save(img_url)
        return 'OK'
    except Exception as e:
        return e


def write_new_likes():
    current_date = datetime.date.today()
    sesion = db_session.create_session()
    conn = db_session.create_coon()
    for project in sesion.query(Projects).all():
        values = {'rates_' + str(i): getattr(project, 'rates_' + str(i)) for i in range(1, 6)}
        print('values', values)
        values.update({'project_id': project.id, 'avg_rate': project.avg_rate, 'date': current_date})
        ins = likes_in_day_table.insert().values(**values)
        conn.execute(ins)
    conn.close()


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
