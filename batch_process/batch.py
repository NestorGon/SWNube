from celery import Celery
from pydub import AudioSegment
import requests
import os
from google.cloud import storage

celery = Celery(__name__, broker='redis://localhost:6379/00')

@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,in_ext,out_ext):
    print(in_route)
    print(in_route[1::])
    print(out_route)
    print(1)
    storage_client = storage.Client()
    bucket = storage_client.bucket("swnube30")
    blob = bucket.blob(in_route)
    blob.download_to_filename("{}".format(in_route))
    AudioSegment.from_file("{}".format(in_route),format=in_ext).export("{}".format(out_route), format=out_ext)
    blob = bucket.blob(out_route)
    blob.upload_from_filename(out_route)
    os.remove(in_route)
    os.remove(out_route)
    os.rmdir(task_id)
    print(2)
    r = requests.post(f'http://{os.environ.get("API_INSTANCE_IP")}:5000/api/tasks/{task_id}/processed')
    print(f'Response: {r.status_code}')
