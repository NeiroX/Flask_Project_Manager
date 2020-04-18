import sys
from models import Projects, project_tag_table, Tags
from db_session import global_init, create_coon, create_session
import argparse
import os
import time

global_init("db.sqlite")

print('Working analization')
parser = argparse.ArgumentParser()
parser.add_argument('project_id', nargs=1, type=int)
parser.add_argument('--editing', action='store_true', default=False)
args = parser.parse_args()
project_id = args.project_id
sesion = create_session()
project = sesion.query(Projects).get(project_id)  # type: Projects
if args.editing:
    sesion = create_session()
    tags = sesion.query(project_tag_table).get(project.id).all()
    if tags:
        conn = create_coon()
        deliting_elements = project_tag_table.delete().where(Projects.id == project.id)
        sesion.execute(deliting_elements)
        sesion.commit()
probable_tags = []
all_tags = set()
t = time.time()
with open(os.path.join(os.getcwd(), 'data/main_tags.txt')) as main_tags_file:
    for word in main_tags_file.readlines():
        all_tags.add(word.strip())
formatted_words = project.filter_text()
print('Отформатированный текст:', formatted_words)
for word in formatted_words:
    word = word.strip()
    if (word.startswith('~') and word[1:]in all_tags)or word in all_tags:
        probable_tags.append(word.replace('~',''))
    elif word.startswith('~'):
        probable_tags.append(word[1:])
print('Теги проекта:', probable_tags)
print(time.time() - t)
for name_tag in probable_tags:
    tag = sesion.query(Tags).filter(Tags.interest == name_tag).first()
    if not tag:
        tag = Tags(interest=name_tag)
        sesion = create_session()
        sesion.add(tag)
        sesion.commit()
        sesion.close()
        tag = sesion.query(Tags).filter(Tags.interest == name_tag).first()
    if tag:
        conn = create_coon()
        ins = project_tag_table.insert().values(project_id=project.id, tag_id=tag.id)
        conn.execute(ins)
