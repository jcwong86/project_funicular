from app import app, main, db
from emails import send_file_ready_notification
from models import Request
from decorators import async
import uuid

def master_process(email, GTFS_url, GTFS_description, agency_id):
	log_request(email, GTFS_url, GTFS_description, agency_id)
	if check_for_active_request() == False:
		process_queue()

def log_request(email, GTFS_url, GTFS_description, agency_id):
	unique_string = str(uuid.uuid4())
	req = Request(GTFS_url, GTFS_description, agency_id, email, unique_string)
	db.session.add(req)
	db.session.commit()
	print 'Request logged!'

@async
def process_queue():
	while get_queue().first() != None:
		process_next_request(get_queue().first())

def process_next_request(req):
	req.begin_processing()
	main.go(req.gtfs_url, req.agency_id, req.uuid)
	print 'Output files created!'
	req.finish_processing()
	with app.app_context():
		send_file_ready_notification(req.email, req.gtfs_description, req.uuid)

def get_queue():
	return Request.query.filter_by(status = 0).order_by(Request.request_time)

def check_for_active_request():
	if Request.query.filter_by(status = 1).first() == None:
		print 'No active request.'
		return False
	else:
		print 'Active request exists.'
		return True
