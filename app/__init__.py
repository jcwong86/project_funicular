from flask import Flask
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjsunix

app = Flask(__name__, static_folder = 'static')
app.config.from_object('config')
app.jinja_env.globals['momentjsunix'] = momentjsunix

db = SQLAlchemy(app)
mail = Mail(app)

from app import views, models