from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(name="start_conversion")
def start_conversion():
    print('background task starting')