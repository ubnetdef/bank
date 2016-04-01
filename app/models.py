from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	password = db.Column(db.String(255))
	enabled = db.Column(db.Boolean)

class Session(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	session = db.Column(db.String(255), unique=True)
	time = db.Column(db.DateTime)
	ip = db.Column(db.String(15))

class Account(db.Model):
	id = db.Column(db.String(10), index=True, unique=True)

	""" Allow a user to have many accounts """
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.Relationship('User', 
		backref=db.backref('accounts', lazy='dynamic'))

	balance = db.Column(db.Float)
	pin = db.Column(db.Integer)

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	src = db.Column(db.String(10))
	dst = db.Column(db.String(10))
	amount = db.Column(db.Float)
	time = db.Column(db.DateTime)

class Log(db.Model):
	id = db.Column(db.Integer)
	type = db.Column(db.Integer)
	time = db.Column(db.DateTime)
	data = db.Column(db.Text)