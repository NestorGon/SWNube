from celery import Celery
from pydub import AudioSegment
import requests

celery = Celery('tasks', broker='redis://redis-container:6379/0')

@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,in_ext,out_ext):
    print(in_route)
    print(in_route[1::])
    print(out_route)
    AudioSegment.from_file("../{}".format(in_route),format=in_ext).export("../{}".format(out_route), format=out_ext)
    r = requests.post(f'http://proyecto-container:5000/api/tasks/{task_id}/processed')
    print(f'Response: {r.status_code}')