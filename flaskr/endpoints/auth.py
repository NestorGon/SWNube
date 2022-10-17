from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from ..models import db, User

class SignUp(Resource):

    def post(self):
        try:
            if User.query.get(request.json['email']) is not None:
                return {'error':"A user with this email already exists"}, 400
            if '@' not in request.json['email']:
                return {'error':'Invalid email'}, 400
            if User.query.filter_by(username=request.json['user']).count() != 0:
                return {'error':"A user with this username already exists"}, 400
            if request.json['password1'] != request.json['password2']:
                return {'error':"Passwords don't match"}, 400
            new_user = User(email=request.json['email'], username=request.json['user'], password=request.json['password1'])
            db.session.add(new_user)
            db.session.commit()
            return {"message":"User created successfully"}
        except:
            return {'error':'Bad request'}, 400


class LogIn(Resource):

    def post(self):
        user = None
        try:
            request.json['email']
            request.json['password']
        except:
            return {'error':'Bad request'}, 400
        user = User.query.get_or_404(request.json['email'])
        if user.password != request.json['password']:
            return {'error':'Bad credentials'}, 401
        token = create_access_token(identity = user.email)
        return {'token':token}