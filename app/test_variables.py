import psycopg2

global bart = "http://gtfs.s3.amazonaws.com/bart-archiver_20140109_0110.zip"
global mta ="http://gtfs.s3.amazonaws.com/mta-new-york-city-transit_20140205_0118.zip"
global mbta = "http://gtfs.s3.amazonaws.com/massachusetts-archiver_20140315_0110.zip"

global james_db = psycopg2.connect(hostname="localhost", database="db", user="postgres", password="password")
global drew_db = psycopg2.connect(hostname="localhost", database="db", user="postgres", password="password")
