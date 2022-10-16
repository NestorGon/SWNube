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
            ext = ''
            if '.' not in filename:
                return {'error': 'Bad filename'}, 400
            else:
                ext = filename.split('.')
                ext = ext[len(ext)-1]
                if ext.upper() not in ['MP3','OGG','WAV']:
                    return {'error': 'Invalid extension'}, 400
            task = Task(name=filename,originalExt=ext,convertedExt=request.form['newFormat'],state=State.UPLOADED,user=str(current_user))
            db.session.add(task)
            db.session.commit()
            task_path = os.path.join(current_app.config['UPLOAD_FOLDER'],str(task.id))
            os.makedirs(task_path)
            original_audio.save(os.path.join(task_path,filename))
            start_conversion.delay()
            return {'message':'Task created successfully','task':tasks_schema.dump(task)}

