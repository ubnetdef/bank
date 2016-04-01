from app import app, respond

@app.route('/transfer')
def transfer():
	"""
	Transfer's money between two accounts. It will
	then add it to the "logs" table
	"""
	return respond("TODO")

@app.route('/giveMoney')
def giveMoney():
	"""
	Like transfer, but the src account is the bank's
	account number (0000000001), and the src account
	does not get subtracted any money
	"""
	return respond("TODO")

@app.route('/transfers')
def transfers():
	"""
	Returns any/all transfers happening between the
	current logged in user, and a given account number.
	This will be utilized by a bot to detect if money has
	been paid
	"""
	return respond("TODO")
