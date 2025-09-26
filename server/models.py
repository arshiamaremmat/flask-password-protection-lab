# server/models.py
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    # Protect password_hash from being read
    @hybrid_property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute.")

    # Setter: hash and store the password
    @password_hash.setter
    def password_hash(self, password: str):
        # flask-bcrypt returns bytes -> decode to str for storage
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Authenticate: compare provided password against stored hash
    def authenticate(self, password: str) -> bool:
        if not self._password_hash:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'User {self.username}, ID: {self.id}'

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
