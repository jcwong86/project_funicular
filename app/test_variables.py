import psycopg2

global bart
global mta
global mbta
global james_db
global drew_db

bart = "http://gtfs.s3.amazonaws.com/bart-archiver_20140109_0110.zip"
mta ="http://gtfs.s3.amazonaws.com/mta-new-york-city-transit_20140205_0118.zip"
mbta = "http://gtfs.s3.amazonaws.com/massachusetts-archiver_20140315_0110.zip"

try:
    james_db = psycopg2.connect(host="localhost", database="db", user="postgres", password="Honduras")
    print "Connected to James's database. Use james_db for object name."
except:
    print "James's database not connected."
    
try:
    drew_db = psycopg2.connect(host="localhost", database="db", user="postgres", password="password")
    print "Connected to Drew's database. Use drew_db for object name."
except:
    print "Drew's database not connected."