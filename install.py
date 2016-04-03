#!/usr/bin/env python
from app import bcrypt, db
from app.models import *

try:
	# Initalize DB
	db.drop_all()
	db.create_all()

	# Create the first user
	hashpw = bcrypt.generate_password_hash("admin")
	user = User("admin", hashpw, is_staff=True)
	account_main = Account("0000001337", user, balance=1000000000.00, pin=1337)

	db.session.add(user)
	db.session.add(account_main)
	db.session.commit()

	print "BankAPI\n"
	print "Username: admin\nPassword: admin\n"
	print "Account: %s\nBalance: %.2f\nPIN: %d" % (account_main.id, account_main.balance, account_main.pin)
except Exception as e:
	print "Error: %s" % (e)