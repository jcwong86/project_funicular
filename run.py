from app import app
from config import APP_DEBUG

if APP_DEBUG == 'true':
	app.run(debug = True)
else:
	app.run()