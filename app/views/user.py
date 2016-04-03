from flask import request
from app import app, db, bcrypt, respond, check_params, validate_session
from app.models import *
from os import urandom
from random import SystemRandom
from binascii import hexlify

@app.route('/register', methods=['POST'])
def register():
	"""
	Simply creates a new user in the User
	model based on the request params
	"""
	try:
		check_params(request, ["username", "password"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	username = str(request.form["username"])
	password = bcrypt.generate_password_hash(request.form["password"])
	newaccount = User(username, password)
	
	try:
		db.session.add(newaccount)
		db.session.commit()
	except:
		return respond("A user with that username already exists", code=400), 400

	return respond("User account created", data={'username': username})

@app.route('/login', methods=['POST'])
def login():
	"""
	Logs the user into the application. Returns
	a session ID which will be used to authenticate
	future sessions
	"""
	try:
		check_params(request, ["username", "password"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	username = str(request.form["username"])
	password = str(request.form["password"])

	user = User.query.filter(User.username == username).first()
	if user == None or not bcrypt.check_password_hash(user.password, password):
		return respond("Unknown or invalid username/password", code=400), 400
	
	# Create a session
	session = Session(hexlify(urandom(50)), user, request.remote_addr)
	try:
		db.session.add(session)
		db.session.commit()
	except:
		return respond("Internal server error has occured", code=101), 500

	return respond("Welcome %s!" % (user.username), data={'session': session.session})

@app.route('/accounts', methods=['POST'])
def accounts():
	"""
	Returns all the accounts owned by the current
	user along with their balance
	"""
	try:
		check_params(request, ["session"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	accountsData = Account.query.filter(Account.user == user).all()
	accounts = []

	for account in accountsData:
		accounts.append({
			'id': account.id,
			'balance': account.balance
		})

	return respond("You currently have %d accounts with the Federal Reserve." % (len(accounts)), data={'accounts': accounts})

@app.route('/balance', methods=['POST'])
def balance():
	"""
	Return's the balance for a specific account. If
	the user is STAFF, then the account does not have
	to be owned by the current user
	"""
	try:
		check_params(request, ["session", "account"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	accountNum = str(request.form["account"])
	account = Account.query.filter(Account.user == user, Account.id == accountNum).first()

	if not account:
		return respond("Unknown or invalid account number", code=400), 400

	return respond("Account %s balance is $%.2f" % (account.id, account.balance), data={'balance': account.balance})

@app.route('/newAccount', methods=['POST'])
def newAccount():
	"""
	Create's a new account under this user. Balance
	is always 0
	"""
	try:
		check_params(request, ["session", "pin"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	gen = SystemRandom()
	accnum = str(''.join(map(str, [gen.randrange(9) for i in range(9)])))
	pin = int(request.form["pin"])
	newaccount = Account(accnum, user, 0.00, pin)
	
	try:
		db.session.add(newaccount)
		db.session.commit()
	except:
		return respond("An internal error has occured. Please try again.", code=400), 400

	return respond("Account created!", data={'account': newaccount.id, 'pin': newaccount.pin})

@app.route('/changePin', methods=['POST'])
def changePin():
	"""
	Change's the PIN for the current user. Must have a
	valid old pin to verify. If user is STAFF, this check
	is waived
	"""
	try:
		check_params(request, ["session", "account","pin"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	accountNum = str(request.form["account"])
	pin = int(request.form["pin"])
	account = Account.query.filter(Account.user == user, Account.id == accountNum).first()

	if not account:
		return respond("Unknown or invalid account number", code=400), 400

	account.pin = pin

	try:
		db.session.commit()
	except:
		return respond("An internal error has occured. Please try again.", code=400), 400

	return respond("PIN for Account %s sucessfully changed!" % (account.id), data={'account': account.id, 'pin': account.pin})
