from celery import Celery
from pydub import AudioSegment

from ..models import Task, State

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,in_ext,out_ext,db):
    AudioSegment.from_file(in_route,format=in_ext).export(out_route, format=out_ext)
    task = Task.query.get(task_id)
    task.state = State.PROCESSED
    db.session.commit()