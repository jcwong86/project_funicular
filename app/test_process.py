# run from app folder!

import json, urllib
from sys import argv
from main import go

def test(agency_id):
	agency_url = 'http://www.gtfs-data-exchange.com/api/agency?agency=' + agency_id
	agency_info = json.load(urllib.urlopen(agency_url))
	data_url = agency_info['data']['datafiles'][0]['file_url']
	go(data_url, 'localhost', 'funicular', 'drewdez', '')

if __name__ == "__main__":
    test(argv[1])