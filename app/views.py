from flask import render_template, redirect, request, url_for, flash, json, jsonify, send_from_directory
from app import app, main, db
from emails import send_file_ready_notification
from models import Request
import urllib, uuid

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',
		title = 'Home')

@app.route('/agency/<agency_id>')
def agency(agency_id):
	agency_url = 'http://www.gtfs-data-exchange.com/api/agency?agency=' + agency_id
	agency_info = json.load(urllib.urlopen(agency_url))
	agency_name = agency_info['data']['agency']['name']
	return render_template('index.html',
		active_agency = agency_info,
		title = agency_name)

@app.route('/get_agencies')
def get_agencies():
	url = 'http://www.gtfs-data-exchange.com/api/agencies'
	agencies_all = json.load(urllib.urlopen(url))
	agencies_us_official = []
	for agency in agencies_all['data']:
		if agency['is_official'] == True and \
			agency['country'] == 'United States' and \
			agency['state'] != "":
			agencies_us_official.append(agency)
	data = {
		'status': 'OK',
		'data': agencies_us_official
	}
	return jsonify(data)

@app.route('/process_selection', methods = ['POST'])
def process_selection():
	# check if user is allowed to submit
	email = request.form['email']
	GTFS_url = request.form['fileURL']
	GTFS_description = request.form['GTFS_description']
	agency_id = request.form['agency_id']
	unique_string = str(uuid.uuid4())
	r = Request(GTFS_url, GTFS_description, email, unique_string)
	db.session.add(r)
	db.session.commit()
	print 'Request logged!'
	main.go(GTFS_url, agency_id, unique_string)
	print 'Output files created!'
	send_file_ready_notification(email, GTFS_description, unique_string)
	print 'Notification sent!'
	return 'OK'

@app.route('/download/<unique_string>')
def download_file(unique_string):
	# check unique_string against database
	file_path = 'output/' + unique_string + '.zip'
	return send_from_directory(app.static_folder, file_path, as_attachment = True)
