import os

# security settings
CSRF_ENABLED = True
SECRET_KEY = os.environ['SECRET_KEY']

# mail server settings
MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_PORT = os.environ['MAIL_PORT']
if MAIL_SERVER != 'localhost':
	MAIL_USERNAME = os.environ['MAIL_USERNAME']
	MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
	MAIL_USE_TLS = os.environ['MAIL_USE_TLS']
	MAIL_USE_SSL = os.environ['MAIL_USE_SSL']
else:
	MAIL_USERNAME = None
	MAIL_PASSWORD = None
APP_EMAIL_ADDRESS = os.environ['APP_EMAIL_ADDRESS']

# administrator settings
ADMINS = ['admin1_email', 'admin2_email']

# database information
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# pgsql2shp command
CONVERTER = os.environ['CONVERTER']

# temporary file output path
OUTPUT_PATH = os.environ['OUTPUT_PATH']

# server name
SERVER_NAME = os.environ['SERVER_NAME']

# Amazon S3 information