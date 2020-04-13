import sys
from models import Projects
import db_session
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('project_id', nargs=1, type=int)
parser.parse_args()
project_id = parser.project_id
sesion = db_session.create_session()
project = sesion.query(Projects).get(project_id)  # type: Projects
probable_tags = {}
all_tags = ()
with open(os.path.join(os.getcwd(), 'data/main_tags.txt'))as main_tags_file:
    for word in main_tags_file.readlines():
        all_tags.add(word.strip())
for word in project.filter_text():
    if word in all_tags:
        probable_tags[word] = []
