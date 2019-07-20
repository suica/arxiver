from celery import Celery
import arxiv
import re
import os

db_address = os.getenv('SQLITE_DB_ADDR','/Users/suicca/Workspace/celery_demo/paper.db')

app = Celery('tasks', broker='sqla+sqlite:///{}'.format(db_address), backend='db+sqlite:///{}'.format(db_address))

arxiv_url_pattern = re.compile('[abs|pdf]/(.*)')


@app.task(name='fetch')
def fetch(paper_id):
    id = arxiv_url_pattern.findall(paper_id)
    if len(id) == 0:
        id = paper_id
    else:
        id = id[0]
    x = arxiv.query(id_list=[id])
    return x


@app.task(name='add')
def add(x, y):
    return x + y
