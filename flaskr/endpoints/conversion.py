from google.cloud import storage
#from celery import Celery
#import celery
from flask import request, send_from_directory
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from shutil import rmtree
from google.cloud import pubsub_v1

from flask import current_app

from ..models import db, Task, TaskSchema, State
#from ..batch_process import start_conversion

topic_id="tasks"
project_id=os.environ.get("PROJECT_ID")
publisher=pubsub_v1.PublisherClient()
topic_path=publisher.topic_path(project_id,topic_id)

tasks_schema = TaskSchema()

#celery_app = Celery(__name__, broker='redis://{}:6379/00'.format(os.environ.get("REDIS_INSTANCE_IP")))

bucket_name = "swnube30"

#@celery_app.task(name="start_conversion")
#def start_conversion(*args):
#    pass

class Tasks(Resource):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        max_retrieve = request.args.get('max')
        order = request.args.get('order') if request.args.get('order') != None else '0'
        user_tasks = Task.query.filter_by(user=current_user).order_by(Task.id if order == '0' else Task.id.desc())
        if max_retrieve != None and int(max_retrieve) >= 0:
            user_tasks = user_tasks.limit(int(max_retrieve))
        return [tasks_schema.dump(task) for task in user_tasks]

    @jwt_required()
    def post(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        current_user = get_jwt_identity()
        original_audio = request.files['audio']
        filename = secure_filename(request.form['filename'])
        in_ext = ''
        out_ext = ''
        allowed_ext = ['MP3','OGG','WAV']
        if '.' not in filename:
            return {'error': 'Bad filename'}, 400
        else:
            in_ext = filename.split('.')
            in_ext = in_ext[len(in_ext)-1]
            out_ext = request.form['newFormat']
            if in_ext.upper() not in allowed_ext or out_ext.upper() not in allowed_ext :
                return {'error': 'Invalid extension. Use .mp3, .ogg or .wav'}, 400
        task = Task(name=filename,originalExt=in_ext.lower(),convertedExt=out_ext.lower(),state=State.UPLOADED,user=str(current_user))
        db.session.add(task)
        db.session.commit()
        task_path = os.path.join(current_app.config['UPLOAD_FOLDER'],str(task.id))
        #os.makedirs(task_path)
        #original_audio.save(os.path.join(task_path,filename))
        in_route = "{}/{}".format(task.id,filename)
        out_route = "{}/{}".format(task.id,filename.replace(f'.{in_ext.lower()}',f'.{out_ext.lower()}'))
        blob = bucket.blob("{}/{}".format(task.id, filename))
        blob.upload_from_file(original_audio)
        #args = (task.id,in_route,out_route,in_ext,out_ext)
        args={"task_id":task.id,"in_route":in_route,"out_route":out_route,"in_ext":in_ext,"out_ext":out_ext}
        data=str(args).encode("utf-8")

        future=publisher.publish(topic_path,data)
        print(future.result())
        #start_conversion.apply_async(args=args, queue="batch")
        #print(task.id,in_route,out_route,in_ext,out_ext)
        return {'message':'Task created successfully','task':tasks_schema.dump(task)}
    

class BackgroundTask(Resource):

    def post(self, task_id):
        task = Task.query.get(task_id)
        task.state = State.PROCESSED
        db.session.commit()
        return {'message':'Updated task'}

class Task2 (Resource):
    #5
    @jwt_required()
    def get(self, task_id):
        current_user = get_jwt_identity()
        task = Task.query.filter_by(id=task_id,user=current_user).first()
        return tasks_schema.dump(task)
        

    #7
    @jwt_required()
    def put(self, task_id):
        current_user = get_jwt_identity()
        task = Task.query.filter_by(id=task_id,user=current_user).first()
        if task:
            if task.state == State.UPLOADED:
                #Borrar el archivo antiguo
                files = current_app.config['UPLOAD_FOLDER']
                os.makedirs(files, exist_ok=True)
                #os.remove(os.path.join(files,str(task.id), task.name.replace(f'.{task.originalExt}',f'.{task.convertedExt}')))
            task.state = State.UPLOADED
            task.convertedExt = request.json.get('newFormat', task.convertedExt)
            db.session.commit()
            #generate new file
            task_path = os.path.join(current_app.config['UPLOAD_FOLDER'])
            in_route = os.path.join(task_path, str(task.id) ,task.name)
            out_route = os.path.join(task_path, str(task.id) ,task.name.replace(f'.{task.originalExt.lower()}',f'.{task.convertedExt.lower()}'))
            args = (task.id,in_route,out_route,task.originalExt,task.convertedExt)
           # start_conversion.apply_async(args=args, queue="batch")
            return tasks_schema.dump(task)
        return {'error':'Task not found'}, 404


    #8
    @jwt_required()
    def delete(self, task_id):
        current_user = get_jwt_identity()
        task = Task.query.filter_by(id=task_id,user=current_user).first()
        if task and task.state == State.UPLOADED:
            #Borrar el archivo antiguo
            files = current_app.config['UPLOAD_FOLDER']
            os.makedirs(files, exist_ok=True)
            rmtree(os.path.join(files,str(task.id)))
            return {'message':'Task Delete succesfully'}, 200
        else:
            return {'error':'Task not found'}, 404


class Download(Resource):

    #6
    @jwt_required()
    def get(self, task_id):
        current_user = get_jwt_identity()
        task = Task.query.filter_by(id=task_id,user=current_user).first()
        files = current_app.config['UPLOAD_FOLDER']
        os.makedirs(files, exist_ok=True)
        return send_from_directory(os.path.join(files,str(task.id)), task.name, as_attachment=True)
        

  
