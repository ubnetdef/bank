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
	
	db.session.commit()
except Exception as e:
	print "Error: %s" % (e)