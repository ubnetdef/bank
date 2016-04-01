from app import app, respond

@app.route('/register')
def register():
	"""
	Simply creates a new user in the User
	model based on the request params
	"""
	return respond("TODO")

@app.route('/login')
def login():
	"""
	Logs the user into the application. Returns
	a session ID which will be used to authenticate
	future sessions
	"""
	return respond("TODO")

@app.route('/accounts')
def accounts():
	"""
	Returns all the accounts owned by the current
	user along with their balance
	"""
	return respond("TODO")

@app.route('/balance')
def balance():
	"""
	Return's the balance for a specific account. If
	the user is STAFF, then the account does not have
	to be owned by the current user
	"""
	return respond("TODO")

@app.route('/newAccount')
def newAccount():
	"""
	Create's a new account under this user. Balance
	is always 0
	"""
	return respond("TODO")

@app.route('/changePin')
def changePin():
	"""
	Change's the PIN for the current user. Must have a
	valid old pin to verify. If user is STAFF, this check
	is waived
	"""
	return respond("TODO")
