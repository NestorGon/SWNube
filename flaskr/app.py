#from flaskr import create_app
from flask_restful import Api
from flask_jwt_extended import JWTManager

from .models import db
from .endpoints import SignUp, LogIn, Tasks, BackgroundTask, Task2, Download
import os

from flask import Flask

def create_app(config_name):
    app = Flask(__name__)  
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@34.68.80.135/postgres"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY']='frase-secreta'
    return app

app = create_app('default')
app_context = app.app_context()
app_context.push()

#if not os.path.exists('../files'):
#    os.makedirs('../files')

app.config["UPLOAD_FOLDER"] = "/nfs/home/files"

db.init_app(app)
db.create_all()

api = Api(app, prefix='/api')
api.add_resource(SignUp, '/auth/signup')
api.add_resource(LogIn, '/auth/login')
api.add_resource(Tasks, '/tasks')
api.add_resource(Task2, '/tasks/<int:task_id>')
api.add_resource(Download, '/download/<int:task_id>')
api.add_resource(BackgroundTask, '/tasks/<int:task_id>/processed')

@app.route('/')
def default():
    return 'Success', 200

jwt = JWTManager(app)
