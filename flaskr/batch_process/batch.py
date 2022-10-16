from celery import Celery
from pydub import AudioSegment

from ..models import Task, State

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,format,db):
    print('background task starting')
    AudioSegment.from_mp3(in_route).export(out_route, format=format)
    task = Task.query.get(task_id)
    task.state = State.PROCESSED
    db.session.commit()
    print('background task finished')