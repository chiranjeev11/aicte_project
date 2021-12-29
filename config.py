import os
# # for aws instance
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/trusty-pixel-326015-8d16a9c16e0e.json"
class Config:

	SECRET_KEY = "HEY"

	GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

	SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = 'smtp.googlemail.com' or os.environ.get('MAIL_SERVER')

	MAIL_USE_TLS = True

	MAIL_PORT = int( 587 or os.environ.get('MAIL_PORT'))

	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')

	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	ADMINS = ['chiranjeevkhurana11@gmail.com']

	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')