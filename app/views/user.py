from flask import request
from app import add_log, app, db, bcrypt, respond, check_params, validate_session, delete_session
from app.constants import *
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

		add_log(LOG_USER, "User %s created" % (username))
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

		add_log(LOG_SESSION, "User %s logged in" % (username))
	except:
		db.session.rollback()

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

	add_log(LOG_ACCOUNT, "User %s requested for all his/her account list" % (user.username))

	# Delete their session
	delete_session(request.form["session"])

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
	account = Account.query.filter(Account.id == accountNum).first()

	if (account.user is not user and not user.is_staff) or (not account):
		return respond("Unknown or invalid account number", code=400), 400

	maybeSlack = False
	if user.is_staff and account.user is not user:
		maybeSlack = True

	add_log(LOG_ACCOUNT, "Balance for account #%s requested by %s" % (account.id, user.username), slack=maybeSlack)

	# Delete their session
	delete_session(request.form["session"])

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
	accnum = str(''.join(map(str, [gen.randrange(9) for i in range(10)])))
	pin = int(request.form["pin"])
	newaccount = Account(accnum, user, 0.00, pin)
	
	try:
		db.session.add(newaccount)
		db.session.commit()

		add_log(LOG_ACCOUNT, "User %s created a new account (%s)" % (user.username, accnum))
	except:
		db.session.rollback()

		return respond("An internal error has occured. Please try again.", code=400), 400

	# Delete their session
	delete_session(request.form["session"])

	return respond("Account created!", data={'account': newaccount.id, 'pin': newaccount.pin})

@app.route('/changePin', methods=['POST'])
def changePin():
	"""
	Change's the PIN for the current user. Must have a
	valid old pin to verify. If user is STAFF, this check
	is waived
	"""
	try:
		check_params(request, ["session", "account","pin", "newpin"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	accountNum = str(request.form["account"])
	pin = int(request.form["pin"])
	newpin = int(request.form["newpin"])
	account = Account.query.filter(Account.id == accountNum).first()

	if (account.user != user and not user.is_staff) or (not account):
		return respond("Unknown or invalid account number", code=400), 400

	if int(account.pin) != pin and not user.is_staff:
		return respond("Invalid current account pin", code=400), 400

	account.pin = newpin

	try:
		db.session.commit()

		add_log(LOG_ACCOUNT, "User %s changed account #%s PIN" % (user.username, accountNum), slack=True)
	except:
		db.session.rollback()

		return respond("An internal error has occured. Please try again.", code=400), 400

	# Delete their session
	delete_session(request.form["session"])

	return respond("PIN for Account #%s sucessfully changed!" % (account.id), data={'account': account.id, 'pin': account.pin})
