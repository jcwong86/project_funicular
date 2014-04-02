import main

feed='http://web.mta.info/developers/data/nyct/subway/google_transit.zip'
in_dbhost='funicular2.crlfdv1vx6e1.us-east-1.rds.amazonaws.com'
in_dbname='gtfs_engine'
in_username='jwad'
in_password = '7r4NS17m4p2'
short_agency_name_no_spaces='MTANYCT'

main.go(feed,in_dbhost,in_dbname,in_username,in_password,short_agency_name_no_spaces)