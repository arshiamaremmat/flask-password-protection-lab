# server/app.py
#!/usr/bin/env python3
from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

user_schema = UserSchema()

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

api.add_resource(ClearSession, '/clear', endpoint='clear')

# ---------- NEW: AUTH RESOURCES ----------

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "username and password required"}, 400

        # Create and hash password
        user = User(username=username)
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        # Log in (session)
        session['user_id'] = user.id

        return user_schema.dump(user), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {}, 204
        user = User.query.get(user_id)
        if not user:
            return {}, 204
        return user_schema.dump(user), 200

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "username and password required"}, 400

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user_schema.dump(user), 200

        return {"error": "Invalid credentials"}, 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204

# Register routes
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
