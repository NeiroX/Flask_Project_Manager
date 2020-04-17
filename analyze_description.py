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
args = parser.parse_args()
project_id = args.project_id
sesion = create_session()
project = sesion.query(Projects).get(project_id)  # type: Projects
probable_tags = list()
all_tags = set()
t = time.time()
with open(os.path.join(os.getcwd(), 'data/main_tags.txt')) as main_tags_file:
    for word in main_tags_file.readlines():
        all_tags.add(word.strip())
formatted_words = project.filter_text()
print('Отформатированный текст:', formatted_words)
for word in formatted_words:
    word = word.replace('\r\n', ' ').strip()
    if word in all_tags or word.startswith('~'):
        probable_tags.append(word.replace('~', ''))
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