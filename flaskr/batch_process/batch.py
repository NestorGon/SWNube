from celery import Celery
from pydub import AudioSegment
import requests

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,in_ext,out_ext):
    AudioSegment.from_file(in_route[1::],format=in_ext).export(out_route[1::], format=out_ext)
    r = requests.post(f'http://127.0.0.1/api/tasks/{task_id}/processed')
    print(f'Response: {r.status_code}')