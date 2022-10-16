from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

from flask import current_app

from ..models import db, Task, TaskSchema, State
from ..batch_process import start_conversion

tasks_schema = TaskSchema()

class Tasks(Resource):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user_tasks = Task.query.filter_by(user=current_user)
        return [tasks_schema.dump(task) for task in user_tasks]

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if request.files:
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
            os.makedirs(task_path)
            original_audio.save(os.path.join(task_path,filename))
            in_route = os.path.join(task_path,filename)
            out_route = os.path.join(task_path,filename.replace(f'.{in_ext.lower()}',f'.{out_ext.lower()}'))
            start_conversion.delay(task.id,in_route,out_route,in_ext,out_ext,db)
            return {'message':'Task created successfully','task':tasks_schema.dump(task)}