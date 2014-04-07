from flask.ext.mail import Message
from flask import render_template
from decorators import async
from app import app, mail
from config import APP_EMAIL_ADDRESS

@async
def send_async_email(msg):
	with app.app_context():
		mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = text_body
	msg.html = html_body
	send_async_email(msg)
	print 'Notification sent!'

def send_file_ready_notification(email, GTFS_description, unique_string):
	send_email("Your funicular file is ready!",
		APP_EMAIL_ADDRESS,
		[email],
		render_template('email_notification.txt',
			email = email,
			GTFS_description = GTFS_description,
			unique_string = unique_string),
		render_template('email_notification.html',
			email = email,
			GTFS_description = GTFS_description,
			unique_string = unique_string))