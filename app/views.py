from flask import render_template, redirect, request, url_for, flash, json, jsonify, \
	send_from_directory, abort
from app import app, db
from models import Request
from process_request import master_process
import urllib, os, boto
from config import S3_BUCKET

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',
		title = 'Home')

@app.route('/about_us')
def about_us():
	return render_template('about_us.html',
		title = 'About')

@app.route('/data_output')
def data_output():
	return render_template('data_output.html',
		title = 'Output Data')

@app.route('/FAQ')
def faq():
	return render_template('faq.html',
		title = 'FAQ')

@app.route('/agency')
def select_agency():
	return render_template('agency.html',
		title = 'Select Agency')

@app.route('/agency/<agency_id>')
def agency(agency_id):
	agency_url = 'http://www.gtfs-data-exchange.com/api/agency?agency=' + agency_id
	agency_info = json.load(urllib.urlopen(agency_url))
	agency_name = agency_info['data']['agency']['name']
	return render_template('agency.html',
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
	GTFS_url = request.form['fileURL']
	GTFS_description = request.form['GTFS_description']
	agency_id = request.form['agency_id']
	email = request.form['email']
	user_name = request.form['user_name']
	user_type = request.form['user_type']
	mailing_list = request.form['mailing_list']
	master_process(GTFS_url, GTFS_description, agency_id, email, user_name,
		user_type, mailing_list)
	return 'OK'

@app.route('/download/<unique_string>')
def download_file(unique_string):
	r = Request.query.filter_by(uuid = unique_string).first()
	if r == None:
		return 'Error: The file you requested does not exist.'
	keyName = unique_string + '.zip'
	s3_key = boto.connect_s3().get_bucket(S3_BUCKET, validate = False).get_key(keyName)
	if s3_key == None:
		return 'Error: Your link has expired. Please try submitting your request again.'
	s3_url = s3_key.generate_url(expires_in = 60)
	r.downloads += 1
	db.session.commit()
	return redirect(s3_url)
