from flask import request
from sqlalchemy import or_
from app import add_log, app, db, lock, respond, check_params, validate_session
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

			add_log(LOG_TRANSACTION, "User %s transferred $%.2f from #%s to #%s" % (user.username, amount, srcAccNum, dstAccNum), slack=True)
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

			add_log(LOG_TRANSACTION, "User %s gave $%.2f to %s" % (user.username, amount, dstAccNum), slack=True)
		except:
			db.session.rollback()

			return respond("An internal error has occured. Please try again.", code=400), 400

		# Delete their session
		delete_session(request.form["session"])

		return respond("Transfered %.2f to %s" % (amount, dstAccountNum), data={'account': dstAccount.id, 'balance': dstAccount.balance})

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

	transactions = Transaction.query.filter(or_(Transaction.src == account, Transaction.dst == account)).all()
	cleanTransactions = []

	for t in transactions:
		if t.src == account:
			tType = "SEND"
		else:
			tType = "RECEIVE"

		cleanTransactions.append({
			'type': tType,
			'dst': t.dst.id,
			'src': t.src.id,
			'amount': t.amount,
			'time': t.time,
		})

	add_log(LOG_TRANSACTION, "User %s got the transfer log for #%s" % (user.username, account))

	# Delete their session
	delete_session(request.form["session"])

	return respond("You have done %d transactions." % len(cleanTransactions), data={'transactions': cleanTransactions})
