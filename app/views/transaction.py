from flask import request
from app import app, db, lock, respond, check_params, validate_session
from app.models import *

@app.route('/transfer', methods=['POST'])
def transfer():
	"""
	Transfer's money between two accounts. It will
	then add it to the "logs" table
	"""
	try:
		check_params(request, ["session", "account","dest","amount","pin"])
		user = validate_session(request.form["session"])
	except StandardError as e:
		return respond(str(e), code=400), 400

	srcAccNum = str(request.form["account"])
	dstAccNum = str(request.form["dest"])
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
		dstAccount = Account.query.filter(Account.id == dstAccountNum)
		if not dstAmount:
			return respond("Unknown or invalid destination account number", code=400), 400

		# Now update!
		srcAccount.balance -= amount
		dstAccount.balance += amount

		try:
			db.session.commit()
		except:
			return respond("An internal error has occured. Please try again.", code=400), 400

		return respond("Transfered %.2f to %s" % (amount, dstAccountNum), data={'account': srcAccount.id, 'balance': srcAccount.balance})

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
		return respond("Bad. Go away.", code=400), 400

	with lock:
		# Grab the dst account
		dstAccount = Account.query.filter(Account.id == dstAccountNum)
		if not dstAmount:
			return respond("Unknown or invalid destination account number", code=400), 400

		# Update the balance!
		dstAccount.balance += amount

		try:
			db.session.commit()
		except:
			return respond("An internal error has occured. Please try again.", code=400), 400

		return respond("Transfered %.2f to %s" % (amount, dstAccountNum), data={'account': dstAccount.id, 'balance': srcAccount.balance})

@app.route('/transfers', methods=['POST'])
def transfers():
	"""
	Returns any/all transfers happening between the
	current logged in user, and a given account number.
	This will be utilized by a bot to detect if money has
	been paid
	"""
	return respond("TODO")
