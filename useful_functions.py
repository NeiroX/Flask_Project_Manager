import datetime
from models import likes_in_day_table
import db_session
from models import Projects
from flask import abort
from PIL import Image, ImageDraw
import os
from sqlalchemy.orm import subqueryload
from sqlalchemy import func
import matplotlib.pyplot as plt
import numpy
from models import Comment


def delete_project_image(img_name):
    if img_name.split()[-1] != 'no_project_image.jpg':
        try:
            os.remove(img_name)
        except Exception as e:
            print(e)


def shorten_descriptions(projects):
    print('used shorten_description')
    for project in projects:
        upper_text_length_bound = 64
        current_length = len(project.short_description)
        if current_length <= upper_text_length_bound:
            continue
        else:
            new_description = ''
            for elem in project.short_description.split(' '):
                if len((new_description + ' ' + elem).strip()) <= upper_text_length_bound - 3:
                    new_description += ' ' + elem
                else:
                    if new_description:
                        project.short_description = (new_description + '...').strip()
                    else:
                        project.short_description = project.new_description[:61] + '...'
    return projects


def add_comment_to_project(pr_id):
    sesion = db_session.create_session()
    project = sesion.query(Projects).get(pr_id)
    com = sesion.query(Comment).filter(
        Comment.id == sesion.query(func.max(Comment.id))).first()
    project.comments.append(com)
    sesion.commit()
    sesion.close()
    return


def add_comment(project_id, user_id, text):
    comment = Comment(text=text,
                      creator_id=user_id,
                      project_id=project_id)
    sesion = db_session.create_session()
    sesion.add(comment)
    sesion.commit()
    sesion.close()
    add_comment_to_project(project_id)
    return 'OK'


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
