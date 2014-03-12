from flask import render_template, redirect, url_for, flash, json, jsonify
from app import app, main
import urllib

@app.route('/')
@app.route('/index')
def index():
	flash("Welcome to funicular. In case you're new here, you can get started by \
		selecting an agency below, then clicking on the desired GTFS update.")
	url = 'http://www.gtfs-data-exchange.com/api/agencies'
	agencies_all = json.load(urllib.urlopen(url))
	agencies_us_official = []
	for agency in agencies_all['data']:
		if agency['is_official'] == True and agency['country'] == 'United States':
			agencies_us_official.append(agency)
	return render_template('index.html',
		agencies = agencies_us_official,
		title = 'Home')

@app.route('/get_agencies')
def get_agencies():
	url = 'http://www.gtfs-data-exchange.com/api/agencies'
	agencies_all = json.load(urllib.urlopen(url))
	agencies_us_official = []
	for agency in agencies_all['data']:
		if agency['is_official'] == True and agency['country'] == 'United States':
			agencies_us_official.append(agency)
	data = {
		'status': 'OK',
		'data': agencies_us_official
	}
	return jsonify(data)

@app.route('/get_agency_info/<agency_id>', methods = ['POST'])
def get_agency_info(agency_id):
	url = 'http://www.gtfs-data-exchange.com/api/agency?agency=' + agency_id
	agency_info = json.load(urllib.urlopen(url))
	return jsonify(agency_info)
