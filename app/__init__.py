from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging	
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login = LoginManager(app)

login.login_view = 'login'

mail = Mail(app)

if not app.debug and not app.testing:

		if app.config['MAIL_SERVER']:

			auth = None

			if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:

				auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

			secure = None

			if app.config['MAIL_USE_TLS']:

				secure = ()

			mail_handler = SMTPHandler(

				mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
				fromaddr = 'no-reply@' + app.config['MAIL_SERVER'],
				toaddrs = app.config['ADMINS'],
				subject = 'Rakshak Failure',
				credentials = auth, secure = secure)

			mail_handler.setLevel(logging.ERROR)

			app.logger.addHandler(mail_handler)

		if not os.path.exists('logs'):

			os.mkdir('logs')

			# Rotate file ensures that log file do not grow too large.
			# log file size will be 10kb and for backup 10 log files will be there.
			file_handler = RotatingFileHandler('logs/rakshak.log', maxBytes=10240, backupCount=10)

			# format that includes the timestamp, the logging level, the message and the source file and line number from where the log entry originated.
			file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s in [in %(pathname)s : %(lineno)d]'))

			file_handler.setLevel(logging.INFO)

			app.logger.addHandler(file_handler)

			app.logger.setLevel(logging.INFO)

			app.logger.info('Rakshak startup')

		if app.config['LOG_TO_STDOUT']:

			stream_handler = logging.StreamHandler()
			stream_handler.setlevel(logging.INFO)
			app.logger.addHandler(stream_handler)

		else:

			if not os.path.exists('logs'):

				os.mkdir('logs')
			file_handler = RotatingFileHandler('logs/rakshak.log', maxBytes=10240, backupCount=10)
			file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s in [in %(pathname)s:%(lineno)d]'))
			file_handler.setLevel(logging.INFO)
			app.logger.addHandler(file_handler)



from app import routes