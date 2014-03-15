from flask import render_template, redirect, request, url_for, flash, json, jsonify
from app import app, main
from emails import send_file_ready_notification
import urllib, uuid

@app.route('/')
@app.route('/index')
def index():
	agency_id = request.args.get('agency')
	agency_info = None
	if agency_id != None:
		agency_url = 'http://www.gtfs-data-exchange.com/api/agency?agency=' + agency_id
		agency_info = json.load(urllib.urlopen(agency_url))
		title = agency_info['data']['agency']['name']
	else:
		title = 'Home'
	return render_template('index.html',
		active_agency = agency_info,
		title = title)

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
	GTFS_description = request.form['GTFS_description']
	fileURL = request.form['fileURL']
	unique_string = str(uuid.uuid4())
	# add submission record to database
	# process GTFS data!!!
	send_file_ready_notification(email, GTFS_description, unique_string)
	return 'OK'

@app.route('/download/<unique_string>')
def download_file(unique_string):
	# check unique_string against database
	return "placeholder for file download"