from flask import Flask
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjsunix
from config import ADMINS, MAIL_SERVER, MAIL_PORT_LOGGING, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__, static_folder = 'static')
app.config.from_object('config')
app.jinja_env.globals['momentjsunix'] = momentjsunix

db = SQLAlchemy(app)
mail = Mail(app)

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT_LOGGING), 'no-reply@' + MAIL_SERVER, ADMINS, 'funicular error', credentials, ())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/funicular.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('funicular startup')

from app import views, models
