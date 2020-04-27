import sys
from models import Projects, project_tag_table, Tags
from db_session import global_init, create_coon, create_session
import argparse
import os
import time


# Функция, которая анализирует краткое описание на ключевые слова и добавляет их в бд
def analyze_description(pr_id, is_editing=False):
    '''Функция, которая анализирует краткое описание на ключевые слова и добавляет их в бд'''
    #Подключаемся к бд, достаем проект и анализируем его краткое содержание
    global_init("db.sqlite")
    project_id = pr_id
    sesion = create_session()
    project = sesion.query(Projects).get(project_id)  # type: Projects
    if is_editing:
        sesion = create_session()
        tags = sesion.query(project_tag_table).get(project.id).all()
        if tags:
            deliting_elements = project_tag_table.delete().where(Projects.id == project.id)
            sesion.execute(deliting_elements)
            sesion.commit()
    probable_tags = []
    all_tags = set()
    #Анализ - проход по всем словам и проверка есть ли оне в файле с тегами или начинаются ли они на ~
    #Если есть или начинаются - добавить их к тегам проекта
    with open(os.path.join(os.getcwd(), 'data/main_tags.txt')) as main_tags_file:
        for word in main_tags_file.readlines():
            all_tags.add(word.strip())
    formatted_words = project.filter_text()
    for word in formatted_words:
        word = word.strip()
        if (word.startswith('~') and word[1:] in all_tags) or word in all_tags:
            probable_tags.append(word.replace('~', ''))
        elif word.startswith('~'):
            probable_tags.append(word[1:])
    return probable_tags
