#!/usr/bin/env python
import config
from app import bcrypt, db
from app.models import *

try:
	# Initalize DB
	db.drop_all()
	db.create_all()

	# Create the accounts
	for u in config.ACCOUNTS:
		hashpw = bcrypt.generate_password_hash(u.password)
		user = User(u.username, hashpw, is_staff=u.staff)
		account = Account(u.account.id, user, balance=u.balance, pin=u.account.pin)

		db.session.add_all([
			user,
			account
		])

		print('Created Account: Username: {} // Password: {} // Staff: {} // Account: {} // PIN: {} // Balance: {}'.format(
			u.username, u.password, u.staff, u.account.id, u.account.pin, u.balance))
	
	db.session.commit()
except Exception as e:
	print "Error: %s" % (e)