from config import TEAM_ACCOUNT_MAPPINGS, WHITE_TEAM_ACCOUNT, AMOUNT_PER_SERVICE_UP
from flask import request
from sqlalchemy import or_
from app import add_log, app, bcrypt, db, lock, respond, check_params, validate_session, delete_session
from app.constants import *
from app.models import *

@app.route('/transfer', methods=['POST'])
def transfer():
	"""
	Transfer's money between two accounts. It will
	then add it to the "logs" table
	"""
	try:
		check_params(request, ["session", "src","dst","amount","pin"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	srcAccNum = str(request.form["src"])
	dstAccNum = str(request.form["dst"])
	amount = float(request.form["amount"])
	pin = int(request.form["pin"])

	# Funny guy, eh?
	if pin <= 0:
		return respond("Funny guy, eh?", code=400), 400

	if amount <= 0:
		add_log(LOG_HACKING, "User %s tried to hack the BankAPI by sending negative amounts." % (user.username), slack=True)
		return respond("Trying to break the bank, eh? That's a paddlin.", code=400), 400

	with lock:
		# First get the source account
		srcAccount = Account.query.filter(Account.user == user, Account.id == srcAccNum, Account.pin == pin).first()
		if not srcAccount:
			return respond("Unknown or invalid source account number", code=400), 400

		# Does the source account have the money?
		if srcAccount.balance < amount:
			return respond("You do not have enough money to transfer %.2f" % (amount), code=400), 400

		# Now get the dst account
		dstAccount = Account.query.filter(Account.id == dstAccNum).first()
		if not dstAccount:
			return respond("Unknown or invalid destination account number", code=400), 400

		# Now update!
		srcAccount.balance -= amount
		dstAccount.balance += amount

		# Create the transaction
		transaction = Transaction(srcAccount, dstAccount, amount)

		try:
			db.session.add(transaction)
			db.session.commit()

			add_log(LOG_TRANSACTION, "User %s transferred $%.2f from #%s to %s (#%s)" % (user.username, amount, srcAccNum, dstAccount.user.username, dstAccNum), slack=True)
		except:
			db.session.rollback()

			return respond("An internal error has occured. Please try again.", code=400), 400

		# Delete their session
		delete_session(request.form["session"])

		return respond("Transfered %.2f to %s" % (amount, dstAccNum), data={'account': srcAccount.id, 'balance': srcAccount.balance})

@app.route('/giveMoney', methods=['POST'])
def giveMoney():
	"""
	Like transfer, but the src account is the bank's
	account number (0000000001), and the src account
	does not get subtracted any money
	"""
	try:
		check_params(request, ["session", "account","amount"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	dstAccountNum = str(request.form["account"])
	amount = float(request.form["amount"])

	if not user.is_staff:
		return respond("Bad. Go away.", code=403), 403

	if amount <= 0:
		return respond("Trying to break the bank, eh? That's a paddlin.", code=400), 400

	with lock:
		# Grab the dst account
		dstAccount = Account.query.filter(Account.id == dstAccountNum).first()
		if not dstAccount:
			return respond("Unknown or invalid destination account number", code=400), 400

		# Update the balance!
		dstAccount.balance += amount

		# Create the transaction
		srcAccount = Account.query.filter(Account.id == WHITE_TEAM_ACCOUNT).first()
		transaction = Transaction(srcAccount, dstAccount, amount)

		try:
			db.session.add(transaction)
			db.session.commit()

			add_log(LOG_TRANSACTION, "User %s gave $%.2f to %s (%s)" % (user.username, amount, dstAccount.user.username, dstAccountNum), slack=True)
		except:
			db.session.rollback()

			return respond("An internal error has occured. Please try again.", code=400), 400

		# Delete their session
		delete_session(request.form["session"])

		return respond("Transfered %.2f to %s" % (amount, dstAccountNum), data={'account': dstAccount.id, 'balance': dstAccount.balance})

@app.route('/internalGiveMoney', methods=['POST'])
def internalGiveMoney():
	"""
	Like giveMoney, but done through the scoring engine.
	"""
	try:
		check_params(request, ["username", "password","team"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	username = str(request.form["username"])
	password = str(request.form["password"])
	team = int(request.form["team"])

	# Check team mappings
	if team not in TEAM_ACCOUNT_MAPPINGS:
		return respond("Bad.", code=400), 400

	dstAccountNum = TEAM_ACCOUNT_MAPPINGS[team].id

	user = User.query.filter(User.username == username).first()
	if user == None or not bcrypt.check_password_hash(user.password, password):
		return respond("Unknown or invalid username/password", code=400), 400

	if not user.is_staff:
		return respond("Bad. Go away.", code=403), 403

	with lock:
		# Grab the dst account
		dstAccount = Account.query.filter(Account.id == dstAccountNum).first()
		if not dstAccount:
			return respond("Unknown or invalid destination account number", code=400), 400

		# Update the balance!
		dstAccount.balance += AMOUNT_PER_SERVICE_UP

		# Create the transaction
		srcAccount = Account.query.filter(Account.id == WHITE_TEAM_ACCOUNT).first()
		transaction = Transaction(srcAccount, dstAccount, AMOUNT_PER_SERVICE_UP)

		try:
			db.session.add(transaction)
			db.session.commit()

			add_log(LOG_TRANSACTION, "Gave $%.2f to %s (%s) for service uptime check" % (AMOUNT_PER_SERVICE_UP, dstAccount.user.username, dstAccountNum))
		except:
			db.session.rollback()

			return respond("An internal error has occured. Please try again.", code=400), 400

		return respond("Transfered %.2f to %s" % (AMOUNT_PER_SERVICE_UP, dstAccountNum), data={'account': dstAccount.id, 'balance': dstAccount.balance})


@app.route('/transfers', methods=['POST'])
def transfers():
	"""
	Returns any/all transfers happening between the
	current logged in user, and a given account number.
	This will be utilized by a bot to detect if money has
	been paid
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

	transactions = Transaction.query.filter(or_(Transaction.src == account, Transaction.dst == account)).order_by(Transaction.time.desc()).all()
	cleanTransactions = []

	for t in transactions:
		if t.src == account:
			tType = "SEND"
		else:
			tType = "RECEIVE"

		cleanTransactions.append({
			'type': tType,
			'dst': t.dstAccount,
			'src': t.srcAccount,
			'amount': t.amount,
			'time': t.time,
		})

	add_log(LOG_TRANSACTION, "User %s got the transfer log for #%s" % (user.username, account.id))

	# Delete their session
	delete_session(request.form["session"])

	return respond("You have done %d transactions." % len(cleanTransactions), data={'transactions': cleanTransactions})
