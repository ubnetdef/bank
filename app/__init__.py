import os
import thread
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
import requests
from threading import Lock

app = Flask(__name__)
app.config.from_object('config')

# Setup extensions
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Setup lock
lock = Lock()

# Setup scheduler
scheduler = BackgroundScheduler()

# Add all the models
from app import models

##########################
# Utility function to    #
# return a JSON Response #
##########################
def respond(message, data={}, code=200):
	response = {
		'code': code,
		'message': message
	}

	if data:
		response.update(data)

	return jsonify(response)

##########################
# Utility function to    #
# return check all POST  #
# params                 #
##########################
def check_params(request, params):
	missing = []
	for param in params:
		if param not in request.form.keys():
			missing.append(param)

	if missing:
		raise StandardError("You are missing the following paramaters: %s" % ', '.join(missing))

##########################
# Utility function to    #
# validate a session     #
##########################
def validate_session(session):
	session = models.Session.query.filter(models.Session.session == session).first()

	if not session:
		raise StandardError("Invalid or expired session!")

	return session.user

##########################
# Utility function to    #
# add a log message      #
##########################
def add_log(logType, message, extra={}):
	data = {
		'message': message
	}

	if extra:
		data.update(extra)

	log = models.Log(logType, data)

	try:
		db.session.add(log)
		db.session.commit()
	except Exception as e:
		print e

##########################
# Utility function to    #
# send to slack          #
##########################
def send_slack(message, extra={}):
	thread.start_new_thread(send_slack_actual, (message, extra))

def send_slack_actual(message, extra):
	# Do nothing if this isn't configured
	if 'SLACK_POST_URI' not in app.config:
		return

	payload = {
		'text': message,
		'link_names': 1
	}

	if extra:
		payload.update(extra)

	requests.post(app.config['SLACK_POST_URI'], json=payload)

##########################
# Clear out all sessions #
# that are 15 minutes old#
##########################
@scheduler.scheduled_job('cron', id='cleanup_sessions', second=0)
def cleanup_sessions():
	print "[CRON] Cleaning up sessions..."
	try:
		ago = datetime.utcnow() - timedelta(minutes=15)

		num = models.Session.query.filter(models.Session.time < ago).delete()
		db.session.commit()

		print "[CRON] Cleaned up %d old sessions" % (num)
	except Exception as e:
		print e
		db.session.rollback()

		print "[CRON] Failure - rollback triggered"

# Grab all the views
from app.views import main, user, transaction
