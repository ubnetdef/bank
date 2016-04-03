from app import db
from datetime import datetime
from json import dump

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(255))
	enabled = db.Column(db.Boolean)
	is_staff = db.Column(db.Boolean)

	def __init__(self, username, password, enabled=True):
		self.username = username
		self.password = password
		self.enabled = enabled

class Session(db.Model):
	__tablename__ = 'sessions'

	id = db.Column(db.Integer, primary_key=True)

	""" Allow a user to have many sessions """
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('User', 
		backref=db.backref('sessions', lazy='dynamic'))

	session = db.Column(db.String(100), unique=True)
	time = db.Column(db.DateTime)
	ip = db.Column(db.String(15))

	def __init__(self, session, user, ip=None):
		self.session = session
		self.user = user
		self.ip = ip
		self.time = datetime.utcnow()

class Account(db.Model):
	__tablename__ = 'accounts'

	id = db.Column(db.String(10), primary_key=True)

	""" Allow a user to have many accounts """
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('User', 
		backref=db.backref('accounts', lazy='dynamic'))

	balance = db.Column(db.Float)
	pin = db.Column(db.Integer)

	def __init__(self, id, user, balance=0.00, pin=0000):
		self.id = id
		self.user = user
		self.balance = balance
		self.pin = pin

class Transaction(db.Model):
	__tablename__ = 'transactions'

	id = db.Column(db.Integer, primary_key=True)
	src = db.Column(db.String(10))
	dst = db.Column(db.String(10))
	amount = db.Column(db.Float)
	time = db.Column(db.DateTime)

	def __init__(self, src, dst, amount):
		self.src = src
		self.dst = dst
		self.amount = amount
		self.time = datetime.utcnow()

class Log(db.Model):
	__tablename__ = 'logs'

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.Integer)
	time = db.Column(db.DateTime)
	data = db.Column(db.Text)

	def __init__(self, type, data=None):
		self.type = type
		self.time = datetime.utcnow()
		self.data = dump(data)