from flask import request
from app import add_log, app, db, respond, check_params, validate_session
from app.models import Log
from json import loads

@app.errorhandler(404)
def error_404(error):
	return respond("Unknown request", code=404), 404

@app.route('/')
def index():
	return "Welcome to the Federal Reserve BankAPI. All actions are logged."

@app.route('/logs', methods=['POST'])
def logs():
	"""
	Returns all information if current user is STAFF
	"""
	try:
		check_params(request, ["session"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	if not user.is_staff:
		return respond("Bad. Go away.", code=403), 403

	logs = Log.query.order_by(Log.time.desc()).all()
	logsSafe = []

	for log in logs:
		logSafe = {
			'id': log.id,
			'type': log.logType,
			'time': log.time,
		}

		logSafe.update(loads(log.data))

		logsSafe.append(logSafe)

	return respond("There are %d log messages." % (len(logs)), data={'logs': logsSafe})
