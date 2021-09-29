from flask import current_app
from app import db, login
import time
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime


class User(UserMixin, db.Model):

	id = db.Column(db.Integer, primary_key = True)

	name = db.Column(db.String(64), index = True)

	email = db.Column(db.String(120), index = True, unique = True)

	password_hash = db.Column(db.String(128))

	audios = db.relationship('Audio', backref='user', lazy='dynamic', cascade='all, delete-orphan')


	def __repr__(self):

		return '<User {}>'.format(self.username)

	def set_password(self, password):

		self.password_hash = generate_password_hash(password)

	def check_password(self, password):

		return check_password_hash(self.password_hash, password)


class Audio(db.Model):

	id = db.Column(db.Integer, primary_key=True)

	audio_file_name = db.Column(db.String(255))

	transcript = db.Column(db.String(255))

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	created_at = db.Column(db.String(255), nullable=False, default=datetime.utcnow)

@login.user_loader
def load_user(id):

	return User.query.get(int(id))