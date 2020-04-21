import sys
from models import Projects, project_tag_table, Tags
from db_session import global_init, create_coon, create_session
import argparse
import os
import time


def analyze_description(pr_id, is_editing=False):
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
