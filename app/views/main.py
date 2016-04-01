from app import app, respond

@app.errorhandler(404)
def error_404(error):
	return respond("Unknown request", 404), 404

@app.route('/')
def index():
	return "Welcome to the Federal Reserve BankAPI."

@app.route('/logs')
def logs():
	"""
	Returns all information if current user is STAFF
	"""
	return respond("TODO")
