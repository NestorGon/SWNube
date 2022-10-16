from datetime import datetime
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
import enum


db = SQLAlchemy()

class State(enum.Enum):
   UPLOADED = 1
   PROCESSED = 2

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(128))
    originalExt = db.Column(db.String(3))
    convertedExt = db.Column(db.String(3))
    state = db.Column(db.Enum(State))
    user = db.Column(db.String, db.ForeignKey("user.email"), nullable = False)

class User(db.Model):
    email = db.Column(db.String(128), primary_key = True)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.name

class TaskSchema(SQLAlchemyAutoSchema):
    state = EnumADiccionario(attribute=("state"))
    class Meta:
         model = Task
         include_relationships = True
         load_instance = True

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
         model = User
         include_relationships = True
         load_instance = True
